[![Build Status](https://travis-ci.org/sesam-community/power-bi.svg?branch=master)](https://travis-ci.org/sesam-community/power-bi)

# Salesforce-Connector

This is a microservice for connecting to the Salesforce restAPI and the Salesforce streaming API with Sesam and getting data for other applications or posting new data to Salesforce.
To connect to the restAPI you need a Basic login token, and to use the streaming API you need OAuth 2.0 credentials.
The streaming API is written to minimize the numbers of quieries to the rest API since this has a limit. The streaming limit is a lot higher, and therefor it is used to look for updates without doing any query.

## Limitations

See the [Salesforce Developer Limits and Allocations Quick Reference](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_overview.htm)

## Supperted queries (per 29.01.20)

- Account
- Campaign
- Case
- Contact
- ContractLineItem
- Entitlement
- Lead
- LiveChatTranscript
- Opportunity
- Quote
- QuoteLineItem
- ServiceAppointment
- ServiceContract
- Task
- WorkOrder
- WorkOrderLineItem

Check Supported [PushTopic Queries](https://developer.salesforce.com/docs/atlas.en-us.api_streaming.meta/api_streaming/supported_soql.htm)

# Authentication

The connector uses two different modules, they use two different authentication modules, so as of now, we need two different authentication setup.


## Generate token for Basic login

If you don't have a security token, you need to login to salesforce and reset your security token, this is done by:

1. Open a browser and navigate to [Salesforce](https://https://login.salesforce.com) (If you going to use sandbox, login to [Salesforce sandbox](https://https://test.salesforce.com)).

2. Select **Your user -> Settings -> My Personal Information -> Reset My Security Token**. Press **Reset security** button, the security token will now be visible, but keep in mind that the old token is now useless, and if you change page again, the security token will disappear.

## Generate OAuth 2.0 credentials

If you don't have credentials for OAuth 2.0 authorization, you need to make an connected app in salesforce.

1. Choose **Options -> Setup -> App Manager**. In the rightupper corner press **New Connected App** .

2. Fill in the required informatin fileds
  - Connected App Name : Name of the app (Do not need to match your connector name)
  - API Name : Name of API (Do not need to match your connector API name)
  - Contact Email : Some e-mail

3. Now you need to check the **Enable OAuth settings** radio button.
  - Callback URL : If you press the **Enable for Device Flow** an example URL shows up, this can be used, or you can use example https://test.salesforce.com
  - Selected OAuth Scope : Full access (full)

4. Fill in the required information fields and press **Save**. Now you get a new window with the "consumer key" and the "consumer secret"

5. You might need to relax on som policies, after you have made your connected app, you will see it in the **App Manager**, push the **downarrow** button on the right an choose **Manage**. On the top of this screen, push the **Edit Policies** button and change the **Permitted Users** to "All users may self-authorize" and change the **IP Relaxation** to "Relax IP restriction"


## Setting up PushTopics for the streaming API

To create a pushTopic for the streaming API to listen to, you need to make a pushTopic, you can either use the notebook in the folder or:

1. Login to salesforce

2. Go to **Options -> Developer Console**.

3. From here you choose **Debug -> Open Execute Anonymous Window**

4. Use this code snippet to make a topic:
* There are two things to take notice here, the .Name and the .Query
  - The .Name are the name of the topic, and would be the name of the topic that you need to subscribe to from the connector, this also need to be unique, so change this according to what topic you are listening to, in this example 'Account' would be the topic listening to.
  - The .Query is in this example subscribing on changes in the Account table. This means that when adding a new topic, the table name after the FROM statment needs to be the table that you would subscribe to. See the [Reference: PushTopic](https://developer.salesforce.com/docs/atlas.en-us.api_streaming.meta/api_streaming/pushtopic.htm) for more information.

```
PushTopic pushTopic = new PushTopic();
pushTopic.Name = 'Account';
pushTopic.Query = 'SELECT Id, Name, Query FROM Account';
pushTopic.ApiVersion = 47.0;
pushTopic.NotifyForOperationCreate = true;
pushTopic.NotifyForOperationUpdate = true;
pushTopic.NotifyForOperationUndelete = true;
pushTopic.NotifyForOperationDelete = true;
pushTopic.NotifyForFields = 'All';
insert pushTopic;
```

5. Push **Execute**

## Example of Sesam system config
```
{
  "_id": "salesforce-connector",
  "type": "system:microservice",
  "authentication": "basic",
  "docker": {
    "environment": {
      "INSTANCE": false,
      "clientPassword": "$SECRET(clientPassword)",
      "clientUsername": "$SECRET(clientUsername)",
      "consumerKey": "$SECRET(consumerKey)",
      "consumerSecret": "$SECRET(consumerSecret)"
    },
    "image": "daniehj/salesforce-connector:bulk4",
    "port": 5000
  },
  "password": "$SECRET(password)",
  "username": "$SECRET(username)",
  "verify_ssl": true
}


```

For the variables stated in the config paste in your personal values inside the quotation signs ("").
 * clientPassword: Salesforce password
 * clietUsername: Salesforcce username
 * consumerKey: The "consumer key" from connected apps
 * consumerSecret: The "consumer secret" from connected apps
 * password: salesforce password.
 * username: This will contain the security token as well as the username, so it need to be written like "token\username"

The  pipe below shows how to get from salesforce through the microservice in the new "salesforce-connector"-system. The pipe takes a url wich contains the name of the salesforce table you want to get data from. To use the streaming functionality, the since parameter must be set.

## Example of Sesam pipe
```
{
  "_id": "salesforce-import",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "salesforce-connector",
    "supports_since": true,
    "url": "/Account"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"],
        ["add", "_id", "_S.Id"]
      ]
    }
  },
  "pump": {
    "mode": "manual"
  }
}


```
