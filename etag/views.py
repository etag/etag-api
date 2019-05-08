from django.shortcuts import render
from rest_framework.authtoken.models import Token
#from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets, filters, status
from rest_framework.renderers import BrowsableAPIRenderer, JSONPRenderer,JSONRenderer,XMLRenderer,YAMLRenderer #, filters
#from rest_framework.settings import api_settings
from rest_framework_csv.parsers import CSVParser
from rest_framework_csv.renderers import CSVRenderer
from .renderer import eventdropsJSONRenderer
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser,FileUploadParser
#from renderer import CustomBrowsableAPIRenderer
from filters import *
from etag.models import *
from serializer import *
#from serializer import AnimalsSerializer,ReaderSerializer,TaggedAnimalSerializer,ReaderLocationSerializer,TagOwnerSerializer,TagReadsSerializer,TagsSerializer,LocationsSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import os, requests,json
#import DjangoModelPermissionsOrAnonReadOnly
import uuid
import csv
from json import loads
from django.http import HttpResponse

class ReadersViewSet(viewsets.ModelViewSet):
    """
    RFID Readers table view set.
    """
    model = Readers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReaderSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = ReadersFilter
    search_fields = ('user', 'description',)
    ordering_fields = '__all__'
    
    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
            if not user:
                return []
            return Readers.objects.filter(user_id=user.id)
        public_tag_readers = TagReads.objects.filter(public=True).values_list('reader_id')
        return Readers.objects.filter(reader_id__in=public_tag_readers)

    def pre_save(self, obj):
        obj.user_id = self.request.user.id

class AnimalsViewSet(viewsets.ModelViewSet):
    """
    RFID Animal table view set.
    """
    model = Animals
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AnimalsSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = AnimalsFilter
    #search_fields = ('user', 'description',)
    ordering_fields = '__all__'
    
class LocationsViewSet(viewsets.ModelViewSet):
    """
    RFID Locations table view set.
    """
    model = Locations
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = LocationsSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = LocationsFilter
    #search_fields = ('user', 'description',)
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
           if not user:
              return []
           private_reader_loc = ReaderLocation.objects.filter(reader_id__user_id=user.id).values_list('location_id').distinct()
           return Locations.objects.filter(location_id__in=private_reader_loc)
        public_reader_ids = TagReads.objects.filter(public=True).values_list('reader_id').distinct()
        public_reader_loc = ReaderLocation.objects.filter(reader_id__in=public_reader_ids).values_list('location_id').distinct()
        return Locations.objects.filter(location_id__in=public_reader_loc)


class ReaderLocationViewSet(viewsets.ModelViewSet):
    """
    Reader Location table view set.
    """
    model = ReaderLocation
    queryset = ReaderLocation.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReaderLocationSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = ReaderLocationFilter
    search_fields = ('start_timestamp','end_timestamp')
    ordering_fields = '__all__'
	
    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
            if not user:
               return []
            return ReaderLocation.objects.filter(reader_id__user_id=user.id)
        public_tag_readers = TagReads.objects.filter(public=True).values_list('reader_id')
        return ReaderLocation.objects.filter(reader_id__in=public_tag_readers)

	
class TaggedAnimalViewSet(viewsets.ModelViewSet):
    """
    Tagged Animal table view set.
    """
    model = TaggedAnimal
    queryset = TaggedAnimal.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TaggedAnimalSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = TaggedAnimalFilter
    ordering_fields = '__all__'
	
    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
            if not user:
                return []
            private_tags = TagReads.objects.filter(public=False,user_id=user.id).values_list('tag_id').distinct()
            return TaggedAnimal.objects.filter(tag_id__in=private_tags)
        public_tags = TagReads.objects.filter(public=True).values_list('tag_id').distinct()
        return TaggedAnimal.objects.filter(tag_id__in=public_tags)

class TagsViewSet(viewsets.ModelViewSet):
    """
    Tags table view set.
    """
    model = Tags
    queryset = Tags.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagsSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter ,filters.OrderingFilter)
    filter_class = TagsFilter
    #search_fields = ('tag_id',)
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
           if not user:
              return []
           user_tags = TagOwner.objects.filter(user_id=user.id).values_list('tag_id').distinct()
           return Tags.objects.filter(tag_id__in=user_tags)
        public_tags = TagReads.objects.filter(public=True).values_list('tag_id').distinct()
        return Tags.objects.filter(tag_id__in=public_tags)
	
class TagOwnerViewSet(viewsets.ModelViewSet):
    """
    TagOwner table view set.
    """
    model = TagOwner
    queryset = TagOwner.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagOwnerSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter ,filters.OrderingFilter)
    filter_class = TagOwnerFilter
    #search_fields = ('tag_id',)
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
            if not user:
               return []
            return TagOwner.objects.filter(user_id=user.id)
        public_tags = TagReads.objects.filter(public=True).values_list('tag_id').distinct()
        return TagOwner.objects.filter(tag_id__in=public_tags)
    
    def pre_save(self, obj):
        obj.user_id = self.request.user.id
 
class TagReadsViewSet(viewsets.ModelViewSet):
    """
    TagReads table view set.
    """
    model = TagReads
    queryset = TagReads.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagReadsSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = TagReadsFilter
    search_fields = ('tag_id')
    ordering_fields = '__all__'
	
    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
            if not user:
                return []
            else :
                return TagReads.objects.filter(user_id = user.id)
        return TagReads.objects.filter(public=True)

    def pre_save(self, obj):
        obj.user_id = self.request.user.id

class AnimalHitReaderViewSet(viewsets.ModelViewSet):
    """
    RFID AnimalHitReader table view set.
    """
    model = AnimalHitReader
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AnimalHitReaderSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = AnimalHitReaderFilter
    #search_fields = ('user', 'description',)
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
           if not user:
              return []
           else :
              private_tags = TagReads.objects.filter(public=False,user_id=user.id).values_list('tag_id').distinct()
              return AnimalHitReader.objects.filter(tag_id__in=private_tags)
        public_tags = TagReads.objects.filter(public=True).values_list('tag_id').distinct()
        return AnimalHitReader.objects.filter(tag_id__in=public_tags)


class UploadLocationViewSet(viewsets.ModelViewSet):
    """
    RFID UploadLocation table view set.
    """
    model = UploadLocation
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UploadLocationSerializer
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,XMLRenderer,YAMLRenderer)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)
    filter_class = UploadLocationFilter
    #search_fields = ('user', 'description',)
    ordering_fields = '__all__'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_authenticated():
           if not user:
              return []
           else :
              return UploadLocation.objects.filter(user_id = user.id)
        return UploadLocation.objects.all()

    def pre_save(self, obj):
        obj.user_id = self.request.user.id


class fileDataDownloadView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer,JSONPRenderer,CSVRenderer,)

    def get(self, request):
        filetypes = ['tags', 'animals', 'locations']
        filetype = request.GET.get('filetype', None)
        userid = self.request.user.id
        if filetype not in filetypes:
            return Response({"ERROR": "filetype is not one of {0}".format(filetypes)})
        if filetype == 'animals':
            result = Animals.objects.filter(taggedanimal__tag_id__tagowner__user_id=userid).values(
                'taggedanimal__start_time',
                'taggedanimal__end_time',
                'taggedanimal__tag_id',
                'taggedanimal__field_data',
                'field_data',
                'species',
            )
        elif filetype == 'locations':
            result = Locations.objects.filter(readerlocation__reader_id__user_id=userid, ).values(
                'readerlocation__reader_id',
                'readerlocation__reader_id__description',
                'readerlocation__start_timestamp',
                'readerlocation__end_timestamp',
                'latitude',
                'longitude',
                'name'
            )
        elif filetype == 'tags':
            result = TagReads.objects.filter(user_id=userid).values(
                'reader_id', 'tag_id', 'tag_read_time'
            )

        def format_field_names(result, filetype):
            """ This formats the headers to match what is used for csv uploading """
            if filetype == 'animals':
                lookup = {
                    'taggedanimal__start_time': 'tag_startdate',
                    'taggedanimal__end_time': 'tag_enddate',
                    'taggedanimal__tag_id': 'tag_id',
                    'taggedanimal__field_data': 'tag_field_data',  # This field will get replaced by the flatten_field_data function
                    'field_data': 'field_data',  # This field will get replaced by the flatten_field_data function
                    'species': 'animal_species'
                }
            if filetype == 'locations':
                lookup = {
                    'readerlocation__reader_id': 'uuid',
                    'readerlocation__reader_id__description': 'name',  # name and description are backwards in the db
                    'readerlocation__start_timestamp': 'startdate',
                    'readerlocation__end_timestamp': 'enddate',
                    'latitude': 'latitude',
                    'longitude': 'longitude',
                    'name': 'description'  # name and description are backwards in the db
                }
            if filetype == 'tags':
                lookup = {
                    'reader_id': 'uuid',
                    'tag_id': 'tag_id',
                    'tag_read_time': 'timestamp'
                }
            return [lookup.get(name, name) for name in result.field_names]

        def flatten_field_data(result):
            """ yields rows with nested json field data flattened out """
            # FIXME: this incorrectly returns NaN on blank datefields, etc. - should return blank and not NaN
            field_data_names = [name for name in result.field_names if "field_data" in name]
            for row in result:
                for field_data_name in field_data_names:
                    field_data = loads(row[field_data_name])
                    del row[field_data_name]
                    row.update(field_data)
                yield row

        def flatten_field_names(result):
            """ returns column names with nested json flattened out """
            field_data_names = [name for name in result.field_names if "field_data" in name]
            names = {name for name in result.field_names if "field_data" not in name}  # intialize set with non-fielddata fields
            for row in result:
                for field_data_name in field_data_names:
                    for field_name in loads(row[field_data_name]).keys():
                        names.add(field_name)
            return names

        result.field_names = format_field_names(result, filetype)
        if request.accepted_renderer.format == 'csv':
            field_names = flatten_field_names(result)
            flattened_result = flatten_field_data(result)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}_export.csv"'.format(filetype)
            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(flattened_result)

            return response
        else:
            return Response(flatten_field_data(result))


class fileDataUploadView(APIView):
    permission_classes =(IsAuthenticated,)
    #parser_classes = (MultiPartParser, FormParser,FileUploadParser,)
    parser_classes = (FileUploadParser,)
    renderer_classes = (JSONRenderer,)
    #r=requests.post("http://localhost:8080/queue/run/etagq.tasks.tasks.etagDataUpload/.json",data=json.dumps(payload),headers=headers)

    def post(self, request, uploadDirectory="/data/file_upload",format=None):
        #check if uploadDirectory exists
        if not os.path.isdir(uploadDirectory):
            os.makedirs(uploadDirectory)
        username = request.user.username
        user_uploadDirectory = "{0}/{1}".format(uploadDirectory, username)
        if not os.path.isdir(user_uploadDirectory):
            os.makedirs(user_uploadDirectory)
        results=[]
        #upload files submitted
        for key,value in request.FILES.iteritems():
            result={}
            filename= str(uuid.uuid4()) 
            local_file = "{0}/{1}".format(user_uploadDirectory,filename)
            self.handle_file_upload(request.FILES[key],local_file)
            result[key]=local_file
            request.DATA['userid'] = self.request.user.id
            if request.DATA.get("callback",None):
                req = self.callback_task(request,local_file)
                try:
                    result['callback']={"status":req.status_code,"response":req.json()}
                except:
                    result['callback']={"status":req.status_code,"response":req.text}
            results.append(result)
        return Response(results)


    def handle_file_upload(self,f,filename):
        if f.multiple_chunks():
           with open(filename, 'wb+') as temp_file:
                for chunk in f.chunks():
                    temp_file.write(chunk)
        else:
           with open(filename, 'wb+') as temp_file:
                temp_file.write(f.read())

    def callback_task(self,request,local_file):
        #Get Token for task submission
        tok = Token.objects.get_or_create(user=request.user)
        headers = {'Authorization':'Token {0}'.format(str(tok[0])),'Content-Type':'application/json'}
        queue = request.DATA.get("queue","celery")
        tags = request.DATA.get("tags",'') # tags is a comma separated string; Converted to list
        tags= tags.split(',')
        taskname = request.DATA.get("callback")
        payload={"function": taskname,"queue": queue,"args":[local_file,request.DATA],"kwargs":{},"tags":tags}
        components = request.build_absolute_uri().split('/')
        hostname = os.environ.get("api_hostname", components[2])
        #url = "{0}//{1}/api/queue/run/{2}/.json".format(components[0],hostname,taskname)
        url = "http://localhost:8080/queue/run/{0}/.json".format(taskname)
        #print("Success task call")
        return requests.post(url,data=json.dumps(payload),headers=headers)
