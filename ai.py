import os
import json

def get_study_plan(user_prompt, tasks, model_name='gemini-1.5', max_output_tokens=512):
    """
    Generate an AI-powered study plan using the google.genai (Gemini Developer) client.
    Expects GEMINI_API_KEY in environment (preferred) or falls back to GOOGLE_API_KEY for
    backwards compatibility.

    Returns the assistant text on success or an error string prefixed with ⚠️.
    """
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return "⚠️ GEMINI_API_KEY not set. Add it to your environment or .env file (GEMINI_API_KEY=...)."

    # Build the prompt with tasks context
    tasks_text = ""
    if tasks:
        tasks_text = "\n\nCurrent tasks:\n"
        for task in tasks:
            try:
                status = "✓" if task[5] == 'completed' else "○"
                tasks_text += f"- [{status}] {task[2]} (Due: {task[4]})\n"
            except Exception:
                # Defensive formatting if tasks are not in expected shape
                tasks_text += f"- {str(task)}\n"

    prompt_text = (
        "You are a helpful study assistant for university students.\n\n"
        f"A student asked: {user_prompt}\n\n"
        f"{tasks_text}\n"
        "Provide helpful, practical study advice and concrete next steps. "
        "Keep the main recommendations concise and include a short (2-4 item) action list."
    )

    try:
        # Use the modern google.genai client when available
        try:
            from google import genai
        except Exception as imp_e:
            return f"⚠️ google-genai library not installed or import failed: {str(imp_e)}. Install it with: pip install google-genai"

        client = genai.Client(api_key=api_key)

        # Make a lightweight generation call
        resp = client.models.generate_content(
            model=model_name,
            contents=prompt_text,
            config={
                'temperature': 0.2,
                'max_output_tokens': max_output_tokens,
            },
        )

        # Try multiple extraction strategies for different client versions / shapes
        try:
            # Common newer shape: resp.candidates[0].content[0].text
            if hasattr(resp, 'candidates') and resp.candidates:
                cand = resp.candidates[0]
                if hasattr(cand, 'content') and cand.content:
                    first = cand.content[0]
                    if hasattr(first, 'text'):
                        return first.text
                    # sometimes content items are plain strings
                    if isinstance(first, str):
                        return first
            # Older / alternate shape: resp.output[0].content[0].text
            if hasattr(resp, 'output') and resp.output:
                out0 = resp.output[0]
                if hasattr(out0, 'content') and out0.content:
                    c0 = out0.content[0]
                    if hasattr(c0, 'text'):
                        return c0.text
            # Fallback to .text attribute
            if hasattr(resp, 'text') and resp.text:
                return resp.text
        except Exception:
            pass

        # As a last resort, stringify response
        return str(resp)

    except Exception as e:
        # If the client fails due to authentication (API key not accepted), try ADC bearer token
        err_str = str(e)
        auth_issue_indicators = ['401', 'UNAUTH', 'UNAUTHENTICATED', 'ACCESS_TOKEN_TYPE_UNSUPPORTED', 'authentication']
        if any(indicator in err_str.upper() for indicator in [i.upper() for i in auth_issue_indicators]):
            ok, token_or_err = _get_bearer_token_from_adc()
            if ok:
                bearer = token_or_err
                try:
                    rest_resp = _rest_generate_with_bearer(bearer, prompt_text, model_name=model_name, max_output_tokens=max_output_tokens)
                    # If rest_resp looks like an error (prefixed with ⚠️) fall through and return the original error below
                    if isinstance(rest_resp, str) and not rest_resp.startswith('⚠️'):
                        return rest_resp
                except Exception:
                    pass
            # If ADC attempt failed or REST with bearer didn't work, return a helpful message
            return f"⚠️ Gemini client error: {err_str}\n\nDetected authentication issue. Tried Application Default Credentials (ADC) bearer token attempt: {token_or_err if not ok else 'succeeded (used to call REST)'}\nIf you intended to use a Developer API key, ensure GEMINI_API_KEY is a Gemini Developer key (from AI Studio). Otherwise set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON and run 'gcloud auth application-default login' if appropriate."

        # Otherwise surface the original client error so frontend shows it
        return f"⚠️ Gemini client error: {err_str}"


def _get_bearer_token_from_adc():
    """
    Try to obtain a bearer token using Application Default Credentials or a service
    account JSON pointed to by GOOGLE_APPLICATION_CREDENTIALS. Returns (ok, token_or_error).
    """
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        import google.auth
    except Exception as e:
        return False, f'google-auth not installed or import failed: {str(e)}'

    # If GOOGLE_APPLICATION_CREDENTIALS is set, prefer service account file
    sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    try:
        if sa_path:
            creds = service_account.Credentials.from_service_account_file(sa_path, scopes=['https://www.googleapis.com/auth/cloud-platform'])
            creds.refresh(Request())
            return True, creds.token
        # Otherwise try default credentials (gcloud auth application-default login)
        creds, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        creds.refresh(Request())
        return True, creds.token
    except Exception as e:
        return False, f'Failed to obtain ADC token: {str(e)}'


def list_models(api_key):
    """
    Return a tuple (ok, data) where ok is True and data is a list of model ids on success,
    or ok is False and data is the error string on failure.
    This function will attempt API key based listing first, then try OAuth bearer token
    via Application Default Credentials if the API key is rejected.
    """
    try:
        import requests
    except Exception:
        return False, 'requests library not installed'

    urls = [
        f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta2/models?key={api_key}",
    ]

    last_err = None
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
        except Exception as e:
            last_err = str(e)
            continue

        if resp.status_code == 200:
            try:
                j = resp.json()
                if isinstance(j, dict) and 'models' in j:
                    models = [m.get('name') or m.get('displayName') or str(m) for m in j['models']]
                    return True, models
                if isinstance(j, list):
                    return True, j
                return True, j
            except Exception as e:
                return False, f'Invalid JSON response: {str(e)}'

        # If unauthorized/401, try ADC bearer token
        if resp.status_code == 401:
            ok, token_or_err = _get_bearer_token_from_adc()
            if not ok:
                last_err = f'401 and ADC token failed: {token_or_err}'
                continue
            # Try listing with bearer token
            headers = {'Authorization': f'Bearer {token_or_err}'}
            try:
                r2 = requests.get(url.split('?')[0], headers=headers, timeout=10)
                if r2.status_code == 200:
                    try:
                        j = r2.json()
                        if isinstance(j, dict) and 'models' in j:
                            models = [m.get('name') or m.get('displayName') or str(m) for m in j['models']]
                            return True, models
                        if isinstance(j, list):
                            return True, j
                        return True, j
                    except Exception as e:
                        return False, f'Invalid JSON response after ADC token: {str(e)}'
                else:
                    last_err = f'ADC attempt HTTP {r2.status_code}: {r2.text}'
                    continue
            except Exception as e:
                last_err = str(e)
                continue

        last_err = f"HTTP {resp.status_code}: {resp.text}"
        continue

    return False, last_err or 'no-response'


def _rest_generate(api_key, user_prompt, tasks, model_name='text-bison-001'):
    """
    REST fallback to Google Generative Language API. Uses the public REST endpoint and the
    API key (no google-generativeai library required). Returns a string on success or an
    error string prefixed with ⚠️ on failure.
    """
    try:
        import requests
    except Exception:
        return "⚠️ requests not installed"

    # Try both v1 and v1beta2 endpoints (some projects/regions differ)
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generate?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta2/models/{model_name}:generate?key={api_key}",
    ]

    # Build prompt including tasks
    tasks_text = ""
    if tasks:
        tasks_text = "\n\nCurrent tasks:\n"
        for task in tasks:
            status = "✓" if task[5] == 'completed' else "○"
            tasks_text += f"- [{status}] {task[2]} (Due: {task[4]})\n"

    prompt_text = f"You are a helpful study assistant for university students.\n\nA student asked: {user_prompt}\n\n{tasks_text}\nProvide helpful, practical study advice. Keep response concise (3-5 sentences max)."

    payload = {
        "prompt": {"text": prompt_text},
        "maxOutputTokens": 256,
        "temperature": 0.2
    }

    try:
        last_error = None
        for url in endpoints:
            try:
                resp = requests.post(url, json=payload, timeout=10)
            except Exception as e:
                last_error = str(e)
                continue

            if resp.status_code != 200:
                # If 404, attempt to list models (may require OAuth) and include that info
                if resp.status_code == 404:
                    ok, data = list_models(api_key)
                    models_info = data if ok else f'Could not list models: {data}'
                    return f"⚠️ HTTP 404: {resp.text}\nAvailable models/list response: {models_info}"

                # If 401, API key may be insufficient; try obtaining ADC bearer token and retry once
                if resp.status_code == 401:
                    ok_token, token_or_err = _get_bearer_token_from_adc()
                    if ok_token:
                        headers = {'Authorization': f'Bearer {token_or_err}'}
                        try:
                            r2 = requests.post(url.split('?')[0], json=payload, headers=headers, timeout=10)
                            if r2.status_code == 200:
                                j2 = r2.json()
                                # parse similar to success branch
                                if 'candidates' in j2 and isinstance(j2['candidates'], list) and len(j2['candidates']) > 0:
                                    candidate = j2['candidates'][0]
                                    if 'content' in candidate:
                                        if isinstance(candidate['content'], list):
                                            texts = []
                                            for c in candidate['content']:
                                                if isinstance(c, dict) and 'text' in c:
                                                    texts.append(c['text'])
                                                elif isinstance(c, str):
                                                    texts.append(c)
                                            return '\n'.join(texts).strip()
                                        elif isinstance(candidate['content'], str):
                                            return candidate['content'].strip()
                                    if 'output' in candidate:
                                        return str(candidate['output']).strip()
                                    if 'text' in candidate:
                                        return candidate['text'].strip()
                                    if 'output_text' in candidate:
                                        return str(candidate['output_text']).strip()
                                if 'output' in j2:
                                    return str(j2['output']).strip()
                                return json.dumps(j2)
                            else:
                                return f"⚠️ ADC attempt HTTP {r2.status_code}: {r2.text}"
                        except Exception as e:
                            return f"⚠️ ADC retry error: {str(e)}"
                    else:
                        return f"⚠️ HTTP 401: {resp.text}\nADC token attempt failed: {token_or_err}"

                # Return detailed error text prefixed with ⚠️ so app treats it as an AI-layer error
                return f"⚠️ HTTP {resp.status_code}: {resp.text}"

            j = resp.json()
            # Try common response shapes
            if 'candidates' in j and isinstance(j['candidates'], list) and len(j['candidates']) > 0:
                candidate = j['candidates'][0]
                if 'content' in candidate:
                    if isinstance(candidate['content'], list):
                        texts = []
                        for c in candidate['content']:
                            if isinstance(c, dict) and 'text' in c:
                                texts.append(c['text'])
                            elif isinstance(c, str):
                                texts.append(c)
                        return '\n'.join(texts).strip()
                    elif isinstance(candidate['content'], str):
                        return candidate['content'].strip()
                if 'output' in candidate:
                    return str(candidate['output']).strip()
                if 'text' in candidate:
                    return candidate['text'].strip()
                if 'output_text' in candidate:
                    return str(candidate['output_text']).strip()
            if 'output' in j:
                return str(j['output']).strip()
            # If we couldn't parse, return the raw JSON for debugging
            return json.dumps(j)

        # If loop ends with no successful response, return last error info
        return f"⚠️ REST request failed: {last_error or 'no response from endpoints'}"
    except Exception as e:
        return f"⚠️ REST generation error: {str(e)}"


def _rest_generate_with_bearer(bearer_token, prompt_text, model_name='text-bison-001', max_output_tokens=256):
    """
    REST call to Generative Language API using an OAuth bearer token (Authorization: Bearer ...).
    Returns the assistant text on success or an error string prefixed with ⚠️ on failure.
    """
    try:
        import requests
    except Exception:
        return "⚠️ requests not installed"

    endpoints = [
        f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generate",
        f"https://generativelanguage.googleapis.com/v1beta2/models/{model_name}:generate",
    ]

    payload = {
        "prompt": {"text": prompt_text},
        "maxOutputTokens": max_output_tokens,
        "temperature": 0.2,
    }

    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
    }

    last_error = None
    for url in endpoints:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
        except Exception as e:
            last_error = str(e)
            continue

        if resp.status_code == 200:
            try:
                j = resp.json()
                # parse similar shapes as _rest_generate
                if 'candidates' in j and isinstance(j['candidates'], list) and len(j['candidates']) > 0:
                    candidate = j['candidates'][0]
                    if 'content' in candidate:
                        if isinstance(candidate['content'], list):
                            texts = []
                            for c in candidate['content']:
                                if isinstance(c, dict) and 'text' in c:
                                    texts.append(c['text'])
                                elif isinstance(c, str):
                                    texts.append(c)
                            return '\n'.join(texts).strip()
                        elif isinstance(candidate['content'], str):
                            return candidate['content'].strip()
                    if 'text' in candidate:
                        return candidate['text'].strip()
                if 'output' in j:
                    return str(j['output']).strip()
                return json.dumps(j)
            except Exception as e:
                return f"⚠️ Invalid JSON response: {str(e)}"

        # return detailed error for non-200 so calling code can decide next steps
        last_error = f"HTTP {resp.status_code}: {resp.text}"
        continue

    return f"⚠️ REST (bearer) request failed: {last_error or 'no response from endpoints'}"


def get_mock_study_plan(user_prompt, tasks):
    """Fallback mock response (when API not available)"""
    
    total_tasks = len(tasks)
    completed = len([t for t in tasks if t[5] == 'completed'])
    
    mock_response = f"""Here's my AI-powered study plan for you:

Based on your tasks, you have {total_tasks} total assignments with {completed} completed.

📚 Study Tips:
1. Start with your most urgent deadline
2. Break complex topics into smaller chunks
3. Use the Pomodoro technique (25 min focus, 5 min break)
4. Review your completed tasks to build momentum

Regarding your question about '{user_prompt[:30]}...': 
Focus on understanding core concepts first, then practice problems. Good luck! 🎯"""
    
    return mock_response


def test_api_key(api_key=None, model_name='gemini-1.5', timeout=10):
    """
    Test the Gemini/Google Generative API key by making a lightweight request.

    Returns a dict: { ok: bool, message: str, response_preview?: str, error?: str }
    """
    key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not key:
        return {'ok': False, 'error': 'GEMINI_API_KEY (or GOOGLE_API_KEY) not set in environment.'}

    # Try modern google.genai client first
    try:
        try:
            from google import genai
        except Exception as imp_e:
            return {'ok': False, 'error': f'google-genai not installed or import failed: {imp_e}. Install with: pip install google-genai'}

        client = genai.Client(api_key=key)
        prompt = 'Ping test: please reply with the single token ping_ok'

        resp = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                'temperature': 0,
                'max_output_tokens': 8,
            },
        )

        # Try to extract preview
        preview = None
        try:
            if hasattr(resp, 'candidates') and resp.candidates:
                cand = resp.candidates[0]
                if hasattr(cand, 'content') and cand.content:
                    first = cand.content[0]
                    if hasattr(first, 'text'):
                        preview = first.text
                    elif isinstance(first, str):
                        preview = first
            if not preview and hasattr(resp, 'text') and resp.text:
                preview = resp.text
        except Exception:
            preview = str(resp)

        return {'ok': True, 'message': 'API request succeeded — API key appears valid (via google.genai client).', 'response_preview': preview}

    except Exception as e_client:
        # Try REST fallback if available
        try:
            rest = _rest_generate(key, 'Ping test: please reply with the single token ping_ok', tasks=[], model_name='text-bison-001')
            if rest is not None and not str(rest).startswith('⚠️'):
                return {'ok': True, 'message': 'API request succeeded (via REST fallback).', 'response_preview': rest}
        except Exception:
            pass

        return {'ok': False, 'error': f'Client error: {str(e_client)}'}

# End of ai.py

