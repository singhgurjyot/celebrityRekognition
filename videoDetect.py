import boto3
import json
import sys
import time
import pandas as pd

from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv() # Load .env file

class CelebrityRecognition:
    jobId = ''
    rek = boto3.client('rekognition')
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')

    roleArn = ''
    bucket = ''
    video = ''
    startJobId = ''

    sqsQueueUrl = ''
    snsTopicArn = ''
    processType = ''

    def __init__(self, role, bucket, video, dataset_id, table_id):
        self.roleArn = role
        self.bucket = bucket
        self.video = video
        self.dataset_id = dataset_id
        self.table_id = table_id

    def GetSQSMessageSuccess(self):

        jobFound = False
        succeeded = False

        dotLine=0
        while jobFound == False:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'],
                                          MaxNumberOfMessages=10)

            if sqsResponse:

                if 'Messages' not in sqsResponse:
                    if dotLine<40:
                        print('.', end='')
                        dotLine=dotLine+1
                    else:
                        print()
                        dotLine=0
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']:
                    notification = json.loads(message['Body'])
                    rekMessage = json.loads(notification['Message'])
                    print(rekMessage['JobId'])
                    print(rekMessage['Status'])
                    if rekMessage['JobId'] == self.startJobId:
                        print('Matching Job Found:' + rekMessage['JobId'])
                        jobFound = True
                        if (rekMessage['Status']=='SUCCEEDED'):
                            succeeded=True

                        self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                       ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" +
                              str(rekMessage['JobId']) + ' : ' + self.startJobId)
                    # Delete the unknown message. Consider sending to dead letter queue
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl,
                                   ReceiptHandle=message['ReceiptHandle'])


        return succeeded

    def CreateTopicandQueue(self):

        millis = str(int(round(time.time() * 1000)))

        #Create SNS topic

        snsTopicName="AmazonRekognitionExample" + millis

        topicResponse=self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse['TopicArn']

        #create SQS queue
        sqsQueueName="AmazonRekognitionQueue" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)['QueueUrl']

        attribs = self.sqs.get_queue_attributes(QueueUrl=self.sqsQueueUrl,
                                                    AttributeNames=['QueueArn'])['Attributes']

        sqsQueueArn = attribs['QueueArn']

        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn,
            Protocol='sqs',
            Endpoint=sqsQueueArn)

        #Authorize SNS to write SQS queue
        policy = """{{
  "Version":"2012-10-17",
  "Statement":[
    {{
      "Sid":"MyPolicy",
      "Effect":"Allow",
      "Principal" : {{"AWS" : "*"}},
      "Action":"SQS:SendMessage",
      "Resource": "{}",
      "Condition":{{
        "ArnEquals":{{
          "aws:SourceArn": "{}"
        }}
      }}
    }}
  ]
}}""".format(sqsQueueArn, self.snsTopicArn)

        response = self.sqs.set_queue_attributes(
            QueueUrl = self.sqsQueueUrl,
            Attributes = {
                'Policy' : policy
            })

    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)


    # ============== Celebrities ===============
    def StartCelebrityDetection(self):
        response=self.rek.start_celebrity_recognition(Video={'S3Object': {'Bucket': self.bucket, 'Name': self.video}},
            NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})

        self.startJobId=response['JobId']
        print('Start Job Id: ' + self.startJobId)

    def GetCelebrityDetectionResults(self):
        maxResults = 10
        paginationToken = ''
        finished = False
        final_result = []
        while finished == False:
            response = self.rek.get_celebrity_recognition(JobId=self.startJobId,
                                                    MaxResults=maxResults,
                                                    NextToken=paginationToken)
            final_result.append(response['Celebrities'])
            self.result = final_result

            if 'NextToken' in response:
                paginationToken = response['NextToken']
            else:
                finished = True

    def WriteResposeToBigQuery(self):
        client = bigquery.Client()
        dataset_ref = client.dataset(self.dataset_id)
        table_ref = dataset_ref.table(self.table_id)
        job_config = bigquery.LoadJobConfig()

        names = []
        conf = []
        timestamps = []
        video_name = []

        for i in range(0, len(self.result)):
            for j in range(0, len(self.result[i])):
                names.append(self.result[i][j]['Celebrity']['Name'])
                conf.append(self.result[i][j]['Celebrity']['Confidence'])
                timestamps.append(self.result[i][j]['Timestamp'])
                video_name.append(self.video)

        data = pd.DataFrame({'Name': names, 'Confidence': conf, 'Timestamp': timestamps, 'Video_Name': video_name})

        job = client.load_table_from_dataframe(
            data,
            table_ref,
            job_config=job_config,
        )  # API request

        job.result()  # Waits for table load to complete.

        print("Loaded {} rows into BigQuery {}:{}.".format(job.output_rows, self.dataset_id, self.table_id))

def main():
    roleArn = 'YOUR_ROLE_ARN'
    bucket = 'S3_BUCKET_NAME'
    video = 'VIDEO_NAME'

    dataset_id = 'DatasetName'
    table_id = 'TableName'

    analyzer=CelebrityRecognition(roleArn, bucket, video, dataset_id, table_id)
    analyzer.CreateTopicandQueue()

    analyzer.StartCelebrityDetection()
    if analyzer.GetSQSMessageSuccess()==True:
        analyzer.GetCelebrityDetectionResults()

    analyzer.DeleteTopicandQueue()
    analyzer.WriteResposeToBigQuery()


if __name__ == "__main__":
    main()
