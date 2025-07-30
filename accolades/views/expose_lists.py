from rest_framework import viewsets
from rest_framework.response import Response

from accolades.models.accolade import Accolade
from accolades.serializer.accolade import AccoladeSerializer

class ExposeAccoladeLists(viewsets.ViewSet):
    """
    Expose the List of Awards to be filtered by the Frontend. 
    """

    def create(self, request):
        accolades = Accolade.objects.all()
        serializer = AccoladeSerializer(accolades, many=True)
        
        # for accolade in serializer.data:
        #     return Response(accolade)
        return Response(serializer.data)
