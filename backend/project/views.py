from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import Http404, FileResponse, JsonResponse, HttpResponse
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
import numpy as np
from scipy.stats import skew, pearsonr
from collections import Counter
from rest_framework.parsers import MultiPartParser, FormParser
import csv
import json
from django.shortcuts import get_object_or_404
import os
from django.conf import settings
# from dvrs.py import *
from .dvrs import *
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
        print(obj.file)
        return Response({'response': obj}, status=status.HTTP_201_CREATED)
    return Response({}, status=status.HTTP_201_CREATED)

class FileUploadView(generics.CreateAPIView):
    queryset = FileModel.objects.all()
    last_instance = FileModel.objects.last().content
    print(last_instance)
    a = dvrs(last_instance)
    workspace = Workspace.objects.get(workspace=1)
    dashboard =  Dashboard.objects.get(dashboard=1)
    for i in a:
        ctype = i['chart_type'] 
        x=i['top_columns'][0][0].lower()
        y=i['top_columns'][0][1].lower()
        ctitle = str(x)+" vs " +str(y)
        rec_chart = Chart(title= ctitle, x_axis=x, y_axis=y, chart_type= ctype, options='legend,title,color', workspace_name= workspace, dashboard_name=dashboard)
        print(Chart.objects.all())
        rec_chart.save()
        print(rec_chart.chart_id)
    serializer_class = FileModelSerializer
    parser_classes = (MultiPartParser, FormParser)
    

class FileDownloadView(generics.RetrieveAPIView):
    queryset = FileModel.objects.all()
    serializer_class = FileModelSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_path = os.path.join(settings.MEDIA_ROOT, instance.file.name)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = 'inline'
            return response
        raise HttpResponse.Http404("File does not exist")

@api_view(('GET',))
def view_all_files(request):
    if request.method == "GET":
        databases = FileModel.objects.all()
        serializer_class = FileModelSerializer(databases, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)



def view_file(request, pk):
    my_model = get_object_or_404(FileModel, pk=pk)
    file_path = my_model.file.path
    with open(file_path, 'r') as f:
        if file_path.endswith('.csv'):
            file_data = list(csv.reader(f))
            #print(file_data)
            headers = ['id'] + file_data[0]
            rows = []
            for i, row in enumerate(file_data[1:], start=1):
                rows.append({'id': i, **dict(zip(headers[1:], row))})
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'inline; filename={my_model.name}'
            # dvrs(file_data)
            json.dump(rows, response, indent=4)
            
            return response
        elif file_path.endswith('.json'):
            file_data = json.load(f)
            for i, row in enumerate(file_data, start=1):
                row['id'] = i
            response = HttpResponse(json.dumps(file_data, indent=4), content_type='application/json')
            response['Content-Disposition'] = f'inline; filename={my_model.name}'
            return  response

# class WorkspaceViewSet(viewsets.ModelViewSet):
#     queryset = Workspace.objects.all()
#     serializer_class =  WorkspaceSerializer 

#     def get_queryset(self):
#         self.workspace = get_object_or_404(Workspace, name=self.kwargs['workspace'])
#         print(self.workspace)
#         return Workspace.objects.filter(workspace=self.workspace)


@api_view(('GET','POST', 'DELETE', 'PUT'))
def WorkspaceViewSet(request):
    if request.method == 'GET':
        workspace = Workspace.objects.all()
        serializer_class = WorkspaceSerializer(workspace, many=True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    
    elif request.method == 'POST':
        workspace_data = JSONParser().parse(request)
        workspace_serializer = WorkspaceSerializer(data = workspace_data)
        if workspace_serializer.is_valid():
            workspace_serializer.save()
            return JsonResponse(workspace_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Workspace.objects.all().delete()
        return JsonResponse({'message': '{} Workspaces were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)

@api_view(('GET','POST', 'DELETE', 'PUT'))
def DatabaseViewSet(request):
    if request.method == 'GET':
        database = Database.objects.all()
        serializer_class = DatabaseSerializer(database, many=True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)
    

# class WorkspaceViewSet(APIView):
#     workspace = Workspace
#     serializer_class = WorkspaceSerializer(workspace, many=True)

#     def get(self):
#         workspace = Workspace.objects.all()
#         serializer_class = WorkspaceSerializer(workspace, many= True)
#         # user = self.request.user
#         return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)
#         # return Response(Workspace.objects.filter(created_by=user), status=status.HTTP_200_OK)

#     def post(self, request):
#         workspace_data = JSONParser().parse(request)
#         workspace_serializer = WorkspaceSerializer(data = workspace_data)
#         if workspace_serializer.is_valid():
#             workspace_serializer.save()
#             return JsonResponse(workspace_serializer.data, status=status.HTTP_201_CREATED) 
#         return JsonResponse(workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspacePostViewSet(APIView):
    # workspace = Workspace
    # serializer_class = WorkspaceSerializer(workspace, many=True)

    def get(self,request, id):
        item = Workspace.objects.filter(workspace = id)
        # item = Dashboard.objects.get(pk = id)
        serializer_class = WorkspaceSerializer(item, many= True)
        return Response({'response': serializer_class.data}, status=status.HTTP_200_OK)

    def post(self, request, id):
        # workspace_data = JSONParser().parse(request)
        # workspace_serializer = WorkspaceSerializer(data = workspace_data)
        # print(workspace_data, request,id)
        item = Workspace.objects.get(pk=id)
        data = WorkspaceSerializer(instance=item, data=request.data)

        if data.is_valid():
            data.save()
            print(data.data)
            return Response({'response': data.data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(data.errors, status=status.HTTP_400_BAD_REQUEST)

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
        print(item)
        # dashboard_data = JSONParser().parse(request.data)
        # print(dashboard_data)
        data = DashboardSerializer(instance=item, data=request.data)

        if data.is_valid():
            data.save()
            print(data)
            return Response({'response': data.data}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(data.errors, status=status.HTTP_400_BAD_REQUEST)

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
        # dashboard_data =  Dashboard.objects.filter(dashboard =  chart_serializer.dashboard_name)
        # dashboard_serializer =  DashboardSerializer(data = dashboard_data)
        
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
            print(data)
            data.save()
            return Response(data.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_digit(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
    
@api_view(['POST'])
def chart_summary_view(request,id):
    """
    Compute summary statistics, identify patterns and trends, describe the distribution of y values,
    state the type of values (continuous or categorical) for x and y, and state whether they are correlated.
    """
    # print(request)
    # Get input data
    data = json.loads(request.body)
    x_values = data.get('x_values', [])
    y_values = data.get('y_values', [])
    chartid = data.get('chart_id', None)
    x_label = data.get('x_label', None)
    y_label = data.get('y_label', None)
    print(x_values,y_values,chartid,id,x_label,y_label)

    # x_values = request.GET.getlist('x_values', [])
    # y_values = request.GET.getlist('y_values', [])

    # Convert input data to proper types
    x_values = [int(x) if is_digit(x) else float(x) if is_float(x) else x for x in x_values]
    y_values = [int(y) if is_digit(y) else float(y) if is_float(y) else y for y in y_values]

    
    # Determine the data types for x and y
    x_type = "continuous" if isinstance(x_values[0], (int, float)) else "categorical"
    y_type = "continuous" if y_values and isinstance(y_values[0], (int, float)) else "categorical"

    # Calculate summary statistics
    mean_y = np.mean(y_values) if y_type == "continuous" else None
    max_y = np.max(y_values) if y_type == "continuous" else None
    min_y = np.min(y_values) if y_type == "continuous" else None
    range_y = max_y - min_y if y_type == "continuous" else None

    # Identify trends and patterns
    if y_type == "continuous":
        if y_values == sorted(y_values):
            trend = "The "+y_label+" increase consistently."
        elif y_values == sorted(y_values, reverse=True):
            trend = "The "+y_label+" decrease consistently."
        else:
            trend = "There is no consistent trend in the "+y_label+" values."
    else:
        trend = ""

    # Describe the distribution of y values
    if y_type == "continuous":
        if abs(skew(y_values)) > 1:
            distribution = "The "+y_label+" are highly skewed."
        elif abs(skew(y_values)) > 0.5:
            distribution = "The "+y_label+" are moderately skewed."
        else:
            distribution = "The "+y_label+" are roughly symmetric."
    else:
        distribution = ""

    # Calculate the correlation between x and y
    if x_type == "continuous" and y_type == "continuous":
        corr, p_value = pearsonr(x_values, y_values)
        if abs(corr) >= 0.7:
            correlation = "There is a strong positive correlation between "+x_label+" and "+y_label+"."
        elif abs(corr) >= 0.3:
            correlation = "There is a moderate positive correlation between "+x_label+" and "+y_label+"."
        elif abs(corr) > 0:
            correlation = "There is a weak positive correlation between "+x_label+" and "+y_label+"."
        else:
            correlation = "There is no correlation between "+x_label+" and "+y_label+"."
    else:
        correlation = ""
        
    if x_type == "categorical":
        counts = Counter(x_values)
        if len(counts) == 0:
            summary_text_x = ""
        else:
            num_categories = len(counts)
            category_names = list(counts.keys())
            summary_text_x = f"The chart shows {num_categories} unique categories: {', '.join(category_names)}.\n"
            if num_categories > 1:
                summary_text_x += f"The largest category is {max(counts, key=counts.get)}, which makes up {counts[max(counts, key=counts.get)]/sum(counts.values())*100:.2f}% of the pie chart.\n"
            if num_categories > 2:
                sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
                summary_text_x += f"The second and third largest categories are {sorted_counts[1][0]} ({sorted_counts[1][1]/sum(counts.values())*100:.2f}%) and {sorted_counts[2][0]} ({sorted_counts[2][1]/sum(counts.values())*100:.2f}%), respectively.\n"


    # Generate summary text
    summary_text = ""
    if y_type == "continuous":
        summary_text += f"The mean value of {y_label} is {mean_y:.2f}. The maximum value of {y_label} is {max_y}, the minimum value of {y_label} is {min_y}, and the range of {y_label} is {range_y}.\n{trend} \n{distribution} \n{correlation}"
    # elif x_type == "categorical":
    #     summary_text += f"The chart shows {len(x_values)} categories: {', '.join(str(x) for x in x_values)}"
    #     if len(x_values) > 0:
    #         top_parts = sorted(x_values, reverse=True)[:3]
    #         summary_text += f"\nTop 3 categories: {', '.join(str(x) for x in top_parts)}"
    
    # Print and return summary
    if y_values:
        print(summary_text)
        # chart_id = request.GET.get(chartid)
        chart = Chart.objects.get(chart_id=chartid)
        chart.summary = summary_text
        chart.save()
        return Response({'summary': summary_text})
    else:
        print(summary_text_x)
        # chart_id = request.GET.get(chartid)
        chart = Chart.objects.get(chart_id=chartid)
        chart.summary = summary_text_x
        chart.save()
        return Response({'summary': summary_text_x})
    
    # @api_view(['DELETE']) 
#delete chart via chartname
# def delete_chart(request, chartName):
#     try:
#         chart = Chart.objects.get(title=chartName)
#     except Chart.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     chart.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
#delete chart via chartid
def delete_chart(request, chartID):
    try:
        chart = Chart.objects.get(chart_id=chartID)
    except Chart.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    chart.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['DELETE']) 
#delete dashboard via dashboardname
# def delete_dashboard(request, dashboardName):
#     try:
#         dashboard = Dashboard.objects.get(title=dashboardName)
#     except Dashboard.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     dashboard.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
#delete dashboard via dashboardid
def delete_dashboard(request, dashboardID):
    try:
        dashboard = Dashboard.objects.get(dashboard=dashboardID)
    except Dashboard.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    dashboard.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['DELETE']) 
#delete workspace via workspacename
# def delete_workspace(request, workspaceName):
#     try:
#         workspace = Workspace.objects.get(title=workspaceName)
#     except Workspace.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     workspace.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
#delete workspace via workspaceid
def delete_workspace(request, workspaceID):
    try:
        workspace = Workspace.objects.get(workspace=workspaceID)
    except Dashboard.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    workspace.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)