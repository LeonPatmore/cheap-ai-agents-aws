FROM pulumi/pulumi-python:latest

RUN pip install --no-cache-dir pulumi pulumi-aws

RUN pulumi plugin install resource aws
