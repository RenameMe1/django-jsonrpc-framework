from django.http import JsonResponse, HttpResponse
from jsonrpc_framework.logic.dispatcher import ResponseType, BatchResponseType


class ResponseBuilder:
    def build_response(
        self, response: ResponseType | BatchResponseType
    ) -> HttpResponse:
        if response is None:
            return HttpResponse(
                status=204,
            )
        elif isinstance(response, list):
            if response == []:
                return HttpResponse(
                    status=204,
                )

            return JsonResponse(
                status=200,
                data=[item.model_dump() for item in response],
                safe=False,
            )
        else:
            return JsonResponse(
                status=200,
                data=response.model_dump(),
            )
