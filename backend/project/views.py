from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from project.serializer import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, viewsets
from rest_framework.views import APIView
import pandas as pd



from .models import *
from .serializer import *

# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/'
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    if request.method == 'GET':
        data = f"Congratulation {request.user}, your API just responded to GET request"
        return Response({'response': data}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = request.POST.get('text')
        data = f'Congratulation your API just responded to POST request with text: {text}'
        return Response({'response': data}, status=status.HTTP_200_OK)
    return Response({}, status.HTTP_400_BAD_REQUEST)


def create_db(file_path):
    type_of_db = file_path.split(".")
    extension = type_of_db[-1]
    if extension == "json":
        df =  pd.read_json(file_path)
    if extension == 'csv':
        df =  pd.read_csv(file_path)
    
    print(df)
    return df

@api_view(('POST',))
def FileUpload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        obj = models.Database.objects.create(file = file)
        create_db(obj.file)
        return Response({'response': obj}, status=status.HTTP_201_CREATED)
    return Response({}, status=status.HTTP_201_CREATED)


# class WorkspaceViewSet(viewsets.ModelViewSet):
#     queryset = Workspace.objects.all()
#     serializer_class =  WorkspaceSerializer 

#     def get_queryset(self):
#         self.workspace = get_object_or_404(Workspace, name=self.kwargs['workspace'])
#         print(self.workspace)
#         return Workspace.objects.filter(workspace=self.workspace)


# @api_view(('GET','POST', 'DELETE', 'PUT'))
# def WorkspaceViewSet(request):
#     if request.method == 'GET':
#         workspace = Workspace.objects.all()
#         serializer_class = WorkspaceSerializer(workspace, many=True)
#         return Response(serializer_class.data, status=status.HTTP_200_OK)

    
#     elif request.method == 'POST':
#         workspace_data = JSONParser().parse(request)
#         workspace_serializer = WorkspaceSerializer(data = workspace_data)
#         if workspace_serializer.is_valid():
#             workspace_serializer.save()
#             return JsonResponse(workspace_serializer.data, status=status.HTTP_201_CREATED) 
#         return JsonResponse(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     elif request.method == 'DELETE':
#         count = Workspace.objects.all().delete()
#         return JsonResponse({'message': '{} Workspaces were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)

@api_view(('GET','POST', 'DELETE', 'PUT'))
def DatabaseViewSet(request):
    if request.method == 'GET':
        database = Database.objects.all()
        serializer_class = DatabaseSerializer(database, many=True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)
    

class WorkspaceViewSet(APIView):
    workspace = Workspace
    serializer_class = WorkspaceSerializer(workspace, many=True)

    def get_queryset(self):
        user = self.request.user
        return Response(Workspace.objects.filter(created_by=user), status=status.HTTP_200_OK)

    def post(self, request):
        workspace_data = JSONParser().parse(request)
        workspace_serializer = WorkspaceSerializer(data = workspace_data)
        if workspace_serializer.is_valid():
            workspace_serializer.save()
            return JsonResponse(workspace_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspacePostViewSet(APIView):
    # workspace = Workspace
    # serializer_class = WorkspaceSerializer(workspace, many=True)
    def post(self, request, id):
        workspace_data = JSONParser().parse(request)
        workspace_serializer = WorkspaceSerializer(data = workspace_data)
        print(workspace_data, request,id)




# class DashboardViewSet(viewsets.ModelViewSet):
#     queryset = Dashboard.objects.all()
#     serializer_class =  DashboardSerializer

@api_view(('GET','POST', 'DELETE', 'PUT'))
def DashboardViewSet(request):
    if request.method == 'GET':
        dashboard = Dashboard.objects.all()
        serializer_class = DashboardSerializer(dashboard, many=True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        dashboard_data = JSONParser().parse(request)
        dashboard_serializer = DashboardSerializer(data = dashboard_data)
        if dashboard_serializer.is_valid():
            dashboard_serializer.save()
            return JsonResponse(dashboard_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(dashboard_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Dashboard.objects.all().delete()
        return JsonResponse({'message': '{} Dashboards were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


# @api_view(('POST', 'PUT'))
# class DashboardUpdateViewSet(generics.UpdateAPIView):
#     queryset = Dashboard.objects.all()
#     serializer_class = DashboardSerializer

#     def update(self, request, *args, **kwargs):
#         dashboard_data = JSONParser().parse(request)  
#         # Partial update of the data
#         serializer = self.serializer_class(request.user, data=dashboard_data, partial=True)
#         if serializer.is_valid():
#             self.perform_update(serializer)
#         return Response(serializer.data)
    

@api_view(['GET','POST'])
def DashboardUpdateViewSet(request, id):
    if request.method == 'GET':
        item = Dashboard.objects.filter(dashboard = id)
        # item = Dashboard.objects.get(pk = id)
        serializer_class = DashboardSerializer(item, many= True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)

    if request.method == "POST":
        item = Dashboard.objects.get(pk=id)
        data = DashboardSerializer(instance=item, data=request.data)

        if data.is_valid():
            data.save()
            return Response(data.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

# class DashboardUpdateViewSet(APIView):
#     model = Dashboard
#     serializer_clas = DashboardSerializer

#     def get_queryset(self):
#         id = self.request.dashboard
#         return Response(Dashboard.objects.filter(created_by=id), status=status.HTTP_200_OK)

#     def post(self):
#         id = self.response.id 
        
@api_view(('GET','POST', 'DELETE', 'PUT'))
def ChartViewSet(request):
    if request.method == 'GET':
        chart = Chart.objects.all()
        serializer_class = ChartSerializer(chart, many=True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        chart_data = JSONParser().parse(request)
        chart_serializer = ChartSerializer(data = chart_data)
        if chart_serializer.is_valid():
            chart_serializer.save()
            return JsonResponse(chart_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(chart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Chart.objects.all().delete()
        return JsonResponse({'message': '{} Charts were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET','POST'])
def ChartUpdateViewSet(request, id):
    if request.method == 'GET':
        item = Chart.objects.filter(chart_id = id)
        # item = Dashboard.objects.get(pk = id)
        serializer_class = ChartSerializer(item, many= True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)

    if request.method == "POST":
        item = Chart.objects.get(pk=id)
        data = ChartSerializer(instance=item, data=request.data)

        if data.is_valid():
            data.save()
            return Response(data.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)