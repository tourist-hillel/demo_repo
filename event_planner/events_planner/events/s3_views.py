from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from botocore.exceptions import ClientError
from django.shortcuts import render, redirect
from events.boto_client import get_s3_client, UPLOADS_BUCKET_NAME


def upload_files_to_s3(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        content_file = ContentFile(file.read())
        file.seek(0)
        default_storage.save(file.name, ContentFile(file.read()))
    return redirect('s3_files_list')


def s3_files_list(request):
    files = []
    s3_client = get_s3_client()
    errors = []
    continuation_token = None
    content = None
    try:
        while True:
            params = {'Bucket': UPLOADS_BUCKET_NAME}
            if continuation_token:
                params['ContinuationToken'] = continuation_token
                continuation_token = None
            response = s3_client.list_objects_v2(**params)
            content = response.get('Contents', [])
            for file in response.get('Contents', []):
                file_name = file['Key']
                try:
                    file_params = params.copy()
                    file_params['Key'] = file_name
                    presigned_file_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params=file_params,
                        ExpiresIn=40
                    )
                    files.append({
                        'file_name': file_name,
                        'file_url': presigned_file_url,
                        'size': file['Size'],
                        'last_modified': file['LastModified'],
                    })
                except ClientError as e:
                    errors.append(e)
            if response.get('isTruncated'):
                continuation_token = response.get('NextContinuationToken')
            if continuation_token is None:
                break
    except ClientError as e:
        errors.append(e)
    return render(
        request,
        's3_storage/s3_files_list.html',
        {
            'files': files,
            'errors': errors,
            'content': content
        }
    )
