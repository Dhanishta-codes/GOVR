# agent/retry/retry_engine.py

from typing import Callable, Dict, Any

MAX_RETRIES = 2


class RetryResult(dict):
    pass


def retry_with_guardrail(
    *,
    attempt_fn: Callable[[], Any],
    guardrail_fn: Callable[[Any], Dict],
    rewrite_fn: Callable[[Any, Dict], Any],
    max_retries: int = MAX_RETRIES,
) -> RetryResult:

    attempts = 0
    last_guardrail_result = None

    while attempts <= max_retries:

        output = attempt_fn()
        guardrail_result = guardrail_fn(output)

        last_guardrail_result = guardrail_result

        if guardrail_result.get("passed"):

            return {
                "passed": True,
                "output": output,
                "attempts": attempts,
                "guardrail_result": guardrail_result
            }

        attempts += 1

        if attempts > max_retries:
            break

        # rewrite output before retry
        output = rewrite_fn(output, guardrail_result)

    return {
        "passed": False,
        "output": None,
        "attempts": attempts,
        "guardrail_result": last_guardrail_result
    }
