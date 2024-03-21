### Authorization
* The user logs in via Okta/Google. The backend creates an API token for that user and stores it in a simple server session. The user key for that session is returned to the browser as a cookie.

### /data
A dashboard HTML page in the application calls the `/data` endpoint with 2 query parameters, `space` and `months`.

1. With the use of the Google API Token in the session, the application asks the Google Chat API for all the messages in that space in the past X months
2. It also asks Google for all the members in that particular space.
3. Based on the Google user IDs of all the members and all the message authors, it asks the Google People API for details about each user. The user ID has the format `"users/103731680987123456789"`, and comes from the response fields `sender.name` and `member.name`, respectively. Then we try to determine the employee ID from the People API response. It either comes with an `externalId` field of `"type": "Employee ID"`. If that is not present (and it is not always present, we are unsure why), we search for a numerical email alias among the email addresses. We discard all the other information we get from the People API.
4. The backend asks `/jigsaw/people` for details about all of the employee IDs collected in the previous step. For each employee, it reads `role.name`, `grade.name`, `location`, `totalExperience`, `twExperience`, and `gender`. Employee ID remains the identifier of these data sets at runtime.
5. All of this data is finally aggregate, to be returned to the browser. A sample response is shown below.
