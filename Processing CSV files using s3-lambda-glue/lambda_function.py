import boto3
import csv
import io
import json 

# initialise s3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):

    # Get the bucket name and file key from the event
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    try:
        # Read the CSV file from s3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')

        # proecess the CSV content
        processed_rows = []
        reader = csv.reader(io.StringIO(csv_content))
        header = next(reader) # Extract the header row

        for row in reader:
            # Preprocessing : filter out rows with missing values
            if all(row):
                processed_rows.append(row)

        
        # Write processed data back to a new CSV in memory
        output_csv = io.StringIO()
        writer = csv.writer(output_csv)
        writer.writerow(header) # write the header row
        writer.writerows(processed_rows) # write the processed rows
        
        # Upload the processed CSV back to S3

        processed_file_key = file_key.replace('raw/','processed/')
        s3.put_object(
            Bucket='p1-csv-processed-data',
            Key=processed_file_key,
            Body=output_csv.getvalue(),
            #ContentType='text/csv'
        )    
    
        print(f'Processed file uploaded to :{processed_file_key}')

    except Exception as e:
        print(f'Error processing file: {str(e)}')
        raise e

