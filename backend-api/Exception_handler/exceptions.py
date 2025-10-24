import logging as log
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request, Response
from utility.utils import update_headers, get_headers

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    cookies = request.cookies
    headers = request.headers
    msg = str(exc.errors())
    try:
        error_extracted = exc.errors()[0]
        fields = list(error_extracted["loc"])
        fields.remove('body')
        msg = ''
        msg = '.'.join(fields)
        if error_extracted["type"] == "string_pattern_mismatch":
            msg = msg + " is not in correct format"
        if error_extracted["type"] == "missing":
            msg = msg + " is mising from request"
    except Exception as E:
        log.info(E)
    return JSONResponse(
        status_code=400,
        content={
            "errors": msg
        },
        headers=get_headers()
    )