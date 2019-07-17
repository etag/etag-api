from rest_framework.authtoken.models import Token
# Create your views here.
from rest_framework import viewsets, filters, status
from rest_framework.renderers import BrowsableAPIRenderer, JSONPRenderer,JSONRenderer,XMLRenderer,YAMLRenderer #, filters
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.parsers import FileUploadParser
from filters import *
from serializer import *
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import os, requests,json
import uuid
import csv
from json import loads
import pandas as pd
from django.http import HttpResponse
from collections import OrderedDict

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
            private_tags = TagOwner.objects.filter(user_id=user.id).values_list('tag_id').distinct()
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


        def _flatten_single(record, data_fields):
            """ helper function to flatten a record with single values only """
            if type(record) != dict:
                record = loads(record)
            for field in data_fields:
                subfield = loads(record[field])
                for subkey, value in subfield.items():
                    record[subkey] = value
                del record[field]
            return record


        def _flatten_multiple(record, index):
            """ takes a record with nested fields and flattens to a row indicated by index """
            if type(record) != dict:
                record = loads(record)
            else:
                record = record.copy()  # enforce using a copy of record - this is required since we delete fields
            for field in record.keys():
                if "field_data" in field.lower():
                    subfield = loads(record[field])
                    data = {key: value[str(index)] if not pd.isna(value[str(index)]) else ""  # remove NaN from output
                            for key, value in subfield.items()}
                    record.update(data)
                    del record[field]
            return record


        def _nested_count(record):
            """ returns the number of nested records """
            for field in record.keys():
                if "field_data" in field.lower():
                    field_data = loads(record[field])
                    if type(field_data.values()[0]) == dict:
                        return len(field_data.values()[0])
            return 0  # no nested content


        def _sort_by_fieldnames(record, order=[]):
            """ takes a dict and returns an OrderedDict using specified order """
            sorted_record = OrderedDict()
            for item in order:
                sorted_record[item] = record.get(item, None)
            return sorted_record


        def flatten_field_data(result, field_order):
            """ yields rows with nested json field data flattened out
                field_order is a list of field_names to ensure that output is in correct order
            """
            df = pd.DataFrame(result)
            data_fields = [name for name in df.columns if "field_data" in name.lower()]
            for record in loads(df.to_json(orient="records", date_format='iso')):
                nested = _nested_count(record)
                if not nested:
                    yield _sort_by_fieldnames(_flatten_single(record, data_fields), field_order)
                else:  # detected multiple nested records
                    for index in range(nested):
                        yield _sort_by_fieldnames(_flatten_multiple(record, index), field_order)


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
            flattened_result = flatten_field_data(result, field_names)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}_export.csv"'.format(filetype)
            writer = csv.DictWriter(response, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(flattened_result)
            return response
        else:
            field_names = flatten_field_names(result)
            return Response(flatten_field_data(result, field_names))


class templateDownloadView(APIView):
    """ Generates template file for users to use for uploading csv data """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CSVRenderer,)

    def get(self, request):
        filetypes = ['tags', 'animals', 'locations']
        filetype = request.GET.get('filetype', None)
        if filetype not in filetypes:
            return Response({"ERROR": "filetype is not one of {0}".format(filetypes)})
        # TODO: Keep updated with fields used in etagq git repo for uploading
        if filetype == 'animals':
            fields = [
                'ANIMAL_IDENTIFYINGMARKERSTARTDATE',
                'ANIMAL_IDENTIFYINGMARKERENDDATE',
                'ANIMAL_ORIGINALMARKER',
                'ANIMAL_CURRENTMARKER',
                'ANIMAL_SPECIES',
                'TAG_ID',
                'TAG_STARTDATE',
                'TAG_ENDDATE',
            ]
        elif filetype == 'locations':
            fields = [
                'UUID',
                'NAME',
                'STARTDATE',
                'ENDDATE',
                'LATITUDE',
                'LONGITUDE',
                'DESCRIPTION',
            ]
        elif filetype == 'tags':
            fields = [
                "UUID",
                "TAG_ID",
                "TIMESTAMP",
            ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}_template.csv"'.format(filetype)
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()
        return response


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
