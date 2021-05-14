# Celebritiy Recognition

This app uses AWS Rekognition API to recognize celebrities in videos. Amazon Rekognition operations can analyze videos that are stored in Amazon S3 buckets. The video must be encoded using the H.264 codec. The supported file formats are MPEG-4 and MOV. The maximum file size for a stored video is 10GB.


## AWS Prerequisites
----
1. Create a new role for Rekognition from IAM and copy the ARN
    1. Create a new role, select Rekognition and click Next ![image](https://docs.google.com/uc?export=download&id=1-oOOtFoCmL9Tvyk9cusZDiObHRPq9yzL)
    2. Give the role a relevant name ![image](https://docs.google.com/uc?export=download&id=1e9FQUMpUfvVu4_9GQILcG_8Oy_9ZBTvx)
    3. Open the Role and Copy the role ARN for next steps ![image](https://docs.google.com/uc?export=download&id=14DyvfZW4x1F0zkZjJpDFAGjF1zqwr1Tc)

2. Follow the steps to create a new user in IAM
    1. Create a new User and give the user a name. Make sure to check the Programmatic Access checkbox ![image](https://docs.google.com/uc?export=download&id=15hUcxmnds6-ewdSvEOCHVX6-lTlky156)
    2. Attach the following permissions to the user:<br/>
    <b>AmazonSQSFullAccess<br />
    AmazonS3FullAccess<br />
    AmazonRekognitionFullAccess<br />
    AmazonSNSFullAccess</b>
    ![image](https://docs.google.com/uc?export=download&id=18IjDmOWd44eRC7ovCsk_mVkVieXLhVf8)
    3. Copy and save the Client Access Key and Secret Access Key. <b>You won't be able to see the secret after this point. Make sure to copy it!</b>
    ![image](https://docs.google.com/uc?export=download&id=173pFvT01ECN2ZlRcBXzUiwRJR7BaiKJb)

3. Add a new custom inline policy to the user
    1. Click on ```Add inline policy``` ![image](https://docs.google.com/uc?export=download&id=1vN3QLEv9fK3cCwsBkuImRLYku2329MuR)
    2. Go to JSON editor and paste the following contents:<br/>
    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "MySid",
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "YOUR_ROLE_ARN_HERE"
            }
        ]
    }
    ```
    ![image](https://docs.google.com/uc?export=download&id=1qOYjKUUo1A7Ft31OkBq__hzYkRnHBtWV)

4. Go to your CLI and paste the following command:
    ```aws configure```

    Paste the Client Access Key and Secret Key from Step 2.

    Make sure AWS CLI is installed before running this command. Follow <a href="https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html">this</a> to install AWS CLI.


#### AWS setup is complete


## Google Cloud Prerequisites
----
1. Create a new service account and give it owner access. Create a new key and save JSON key it in your system.
    1. ![image](https://docs.google.com/uc?export=download&id=1ed9H6Rx7TSfVtfWDWPHq2VZb9wyJKKU4)
    2. Enter an account name and proceed ![image](https://docs.google.com/uc?export=download&id=1yXCLIJkFqJeeX30-Sdu2Gs0Kn-fYvW36)
    3. Select Owner Permission ![image](https://docs.google.com/uc?export=download&id=1_q7Wv_kClnjnGpOo8LE1FEFyEPm1bpjB)
    4. <b>Go to keys menu and create a new key. Make sure to download the JSON key, you won't be able to download after this point!</b> ![image](https://docs.google.com/uc?export=download&id=1sCjRrnSj1o6EmYExiDW6qYNp_iC3I8-Q)
    5. Download the JSON key and copy the PATH location. ![image](https://docs.google.com/uc?export=download&id=1r_Bw-pODEzOLTWyx4TimpybXCE5N9khb)

2. Create a new file with the name .env and put the following contents in the file:<br/>
```GOOGLE_APPLICATION_CREDENTIALS="PATH TO YOUR JSON KEY FILE"```
3. Create a new dataset in BigQuery and copy the name of dataset. No need to create a new table.

----

Now just paste the Role ARN, S3 bucket name, video name, and BigQuery dataset name in the main function and run the code
