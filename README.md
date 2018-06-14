# DDIY-Solutions

# Editor settings

Developers working on this project should use the following IDE settings:

**atom-prettier:**

* enable `ESLint Integration`
* enable `Single Quotes`
* enable `Bracket Spacing`
* set `Trailing Comma` to `es5`

# AWS Setup

* Create Elastic IP
* Create EC2 Instance
  * Ubuntu Server 16.04 LTS (HVM), SSD Volume Type - ami-10acfb73
  * t2.micro
  * Add HTTP & HTTPS to security group launch-wizard-1
  * Create new private key `t2micro-EC2-instance` and download it
* Associate Elastic IP with running instance
* Create Bucket `ddiy-prod-frontend`
  * Add Bucket policy:
    `{ "Version": "2008-10-17", "Statement": [ { "Sid": "PublicReadForGetBucketObjects", "Effect": "Allow", "Principal": { "AWS": "*" }, "Action": "s3:GetObject", "Resource": "arn:aws:s3:::ddiy-prod-frontend/*" } ] }`
* Create CloudFront distribution
  * Origin Domain Name: Select frontend bucket
  * Compress Objects Automatically: `yes`
* Create IAM User for yourself with `AdministratorAccess`

Update your .ssh/config:

```
Host ddiy-prod
    HostName 13.229.170.29
    Port 22
    User ubuntu
    IdentityFile ~/.ssh/ddiy-solutions/t2micro-EC2-instance.pem
```

Create a deploy key and add it to the github repo:

```
ssh ddiy-prod
sudo apt-get install python
cd .ssh
ssh-keygen -t rsa
chmod 600 id_rsa*
cat id_rsa.pub
# Add key to https://github.com/bitlabstudio/ddiy-solutions/settings/keys
```

Now you can run the ansible script to provision the server

```
cd ansible
ansible-playbook -i hosts server.yml
```

NOTE: At the moment, the letsencrypt role does not work, you can manually
obtain the cert like so:

```
ssh ddiy-prod
cd opt
wget https://dl.eff.org/certbot-auto
chmod a+x ./certbot-auto
sudo ./certbot-auto
# TODO: add certbot crontab
```

# Local Development

* Clone this repo
* make sure that you have Pipenv installed globally

## Start Backend In First Terminal:

```shell
cd backend
pipenv install --dev
pipenv run ./manage.py migrate
pipenv run ./manage.py createsuperuser
# admin / info@example.com / test1234
pipenv run ./manage.py runserver
# browse to localhost:8000/graphiql and try the `{ test }` query
```

## Start Frontend In Second Terminal:

```shell
cd frontend
yarn install
yarn start
# browse to localhost:3000/
```

## TODO: Use nginx setup for localdev

# Testing

In order to run the frontend tests, do the following:

* run `fab test_cypress` in terminal #1
* run `yarn start` in terminal #2
* run `npx cypress open` in terminal #3

# Deployment

## Prerequisites

* Make sure you have awscli installed:
  * `brew install aws-cli`
* Make sure that your `~/.aws/credentials` file has the correct credentials
  under the `[default]` directive

## Deploy Django backend

* `cd` into `backend` folder
* `pipenv install --dev`
* `pipenv run fab prod run_deploy`

## Deploy Razzle frontend

* `cd` into `frontend` folder
* `pipenv install`
* `pipenv run fab prod run_deploy`
