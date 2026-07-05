from django.http import HttpResponse, JsonResponse

from jsonrpc_framework.logic.dispatcher import BatchResponseType, ResponseType


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
