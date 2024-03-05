<div id="top"></div>
<!-- ABOUT THE PROJECT -->

## **LLM on Amazon SageMaker, compatible with AWS GovCloud**

An AWS implementation of a Machine Learning (ML) Large Language Model (LLM) hosting, compatible with GovCloud.

### Built With

[![AWS CDK][AWS]][aws-url]

![cdk][cdk]

<!-- GETTING STARTED -->

## **Getting Started**

### **Prerequisites**

- An AWS account with:
  - An increased quota to deploy one `ml.g4dn.12xlarge` instance for endpoint usage
  - An IAM User or Role with AdministratorAccess policy granted (we recommend restricting access as needed)
- The [AWS CLI installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - export the `AWS_REGION` environment variable
- Typescript, npm, and the [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) cli installed (Required versions found in the package.json file)

### **Deployment**

**_Note: The Amazon SageMaker Endpoint can incur significant cost if left running, be sure to monitor your billing, and destroy the stack via the Clean Up section when done experimenting._**

Configure your AWS credentials, either by exporting your role credentials to the current terminal, or configuring your AWS CLI profile

Next you can run the following commands:

1. `npm install`
2. `npm run build`
3. `cdk bootstrap` (Only for first time running cdk in the account)
4. `cdk deploy`

Once the deployment is completed, you can navigate to `SageMaker Notebook Instances` and open the notebook `Falcon40BNotebook-XXXXXXXXXX` where the X's are randomly generated. From there you can run the notebook cells.

### **Clean Up**

If you have created additional Jupyter notebooks in SageMaker you can download them from the SageMaker notebook instance's IDE before destroying the stack.

When complete you can run:

1. `cdk destroy`

To delete all resources you created.

## **Architecture**

![Architecture](assets/arch.png)

### **Architecture Overview**

To deploy this application, we leverage HuggingFace's prebuilt Text Generation Inference (TGI) Falcon-40b docker image with HuggingFaceSageMakerEndpoint construct(deploy hugging face model to Amazon SageMaker) from [@cdklabs/generative-ai-cdk-constructs](https://github.com/awslabs/generative-ai-cdk-constructs).

The [AWS Deep Learning Containers (DLCs)](https://docs.aws.amazon.com/deep-learning-containers/latest/devguide/what-is-dlc.html) provide the set of Docker images which can be deployed on Amazon SageMaker. This creates a scalable, secure, hosted endpoint for real time inference.

We deploy a SageMaker notebook instance in a private subnet and allow outbound internet connectivity, while controlling inbound connectivity. To enable notebook to AWS Service Endpoint communication, we then use VPC Endpoints powered by AWS PrivateLink. The benefit of using AWS PrivateLink is it allows SageMaker notebook instances to access the SageMaker real-time inference endpoint over the private network IP space.

### **Architecture Details & Technologies**

##### **HuggingFace TGI and Falcon-40b LLM**

Hugging Face's TGI provides a seamless way to deploy LLMs for real-time text generation. It bundles prebuilt Docker containers that handle hosting infrastructure so users can focus on their applications and use-cases.

Falcon-40b features advanced text generation and comprehension capabilities. Boasting 178 billion parameters, Falcon-40b is one of the largest publicly available models. Trained on 1.5 trillion text tokens across English, German, Spanish, French, and other languages, Falcon-40b can fluently generate, summarize, and translate text.

![SagemakerEndpoints]

SageMaker real-time inference endpoints enable low-latency, high-throughput hosting of machine learning models for real-time inference. By using Amazon SageMaker, we can take advantage of the operational efficiencies of using AWS infrastructure and eliminating the undifferentiated heavy-lifting. Amazon SageMaker handles provisioning servers, scaling, monitoring, and availability freeing up the data scientists to work with LLMs.

![SagemakerNotebook]

Amazon SageMaker notebook instances provide a managed and familiar environment, purpose-built for developing and evaluating ML models. Amazon SageMaker provides a painless and cost effective sandbox to prototype capabilities.

Multiple instance types give data scientists flexibility to test small demos or fine-tune LLMs on significant datasets.

![AWSPrivateLink]

Networking components and features of AWS like AWS PrivateLink allow administrators to control private connectivity between VPCs and AWS services securely on AWS without traversing the public internet. This helps enable secure LLM experimentation with datasets.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[SagemakerNotebook]: https://img.shields.io/badge/Amazon%20SageMaker%20Notebook-232F3E?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAMKADAAQAAAABAAAAMAAAAADbN2wMAAAEHElEQVRoBe1ZTWgTQRR+s9k0ibWloIKIl97Em/iDelAvHhREvYTm4lWpUGijVBQ0BRUrtkpBqvci0YueevEk+FstHjzYgwcPHpSimDS1TTbd8c1MMrvZTJLdJGSb0IVu3nzvf/523hRg4/G3B0hV97NTIZI2VqvKtJCJwU6bA/FBu0vN3mhHWncZdJYOxMMuZZsvlpwcJEAfqgy3/Qi0fQLKKUSSEx/5cKWN4iLvkhgyaPfmo3Dq/D8uMzO+k+j6c9Xw1oNRSp9A7NJ9t7rKBFB5n8MAS8TCzL8ByddJqIQnGfURGiGvTQ+qygQoJfuFDdpFCLxB2kDssLT7eWVZ0r3hHzSVL8hLtG6CAv3lRVmZAMRGPnEj+B2AtMFIU2JO6yeHsggJeSevBe3OXMTa04k7vPOWjAAVvahLDNtmT/AGiJ5vQR9Xd6GcQpTCqEMtUIIZK7eQz6YOwMxUL+hGjNPNeFH4ArH4W7emKiVwhRsgoOP2cxPpNUzgmjSaXRHBM0Bf3UYg8EjyGiRw03iAu1BjCWAPjPM4xCJmCeQl5gxQC6eJaTx2wvW2vQTPfChHwJPz6NAiOr3gSaeJwuoEkhMHuY9UPgjiW6xBEWOMhaU5SCS8fG+aGHKpKWUCGPM7LkYKexBAUGLIoHsivfizVGrKn5YyAQzlPQ+HgoYjcABplskHjrGX1rcm6URCg929fbLdKBHpXpXnLBe2lAng2f8Q17UqspzEnEZ3beonJv3mhOttk+UM24WG3eorE3CrzOVocA2I+ceTTnVh65xVXY5zG08gNvwd59cWF75cichV50q6wjaKZ/801xcHOUaGJIYNqoV3QPRihsv4/Ko0Aj2KuCwslBGbq0Ko1ZAyARrJs20SYDkQIhpZRCqH2FaOsdfp0XWxhbJQlAnIAGencoV6gEqMadmfZ3e3EzMwbYdUNH5Svpqx+FUVrxFMnYAXiyZ0o/iZWiq4OK0RrCXsga9MABfsK26jtKgXGDKwqD8hPzY58pOG6NmaPqn2u6ZMHQLKBNDOEYcttmgtzF7Un7vM9u0XDvmWNZUJUI0c4xFQEiTUfIm0gdhxGVW2X1ypSMA/QpkAREfEdOH1AD90mhLzL1al504t6idZzYsHZntRX8AQNkl6DKKJHJfx+aWcQni959yvsai3YeEIu7VY1wmIAp5oWNTTMQwWi3p6XXa2vaiXoD+EcgTwcvU2D0cU9SwBLOoLmD9xVvTamYsYkvfEZW3KsBX1BYz1xUJmfp0X9WSOjxn7/ooHi/oChu12KOqLt80shb0sZvybxz/x2Iv6IubTr3IRYwEvplBpUS8wnwKt5LZDF3F5ugTYlurXkzL0wg1hWQTKKVQmBdDl63/src2kLDQ3CVhX6WXqLQYI8P93tdjrhruqPfAfWXg1BHBE78oAAAAASUVORK5CYII=
[jupyter]: https://img.shields.io/badge/Jupyter_Notebook-232F3E?&logo=jupyter&logoColor=F37626
[SagemakerEndpoints]: https://img.shields.io/badge/Amazon%20SageMaker%20Endpoints-232F3E?logo=data:image/png;base64,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
[aws]: https://img.shields.io/badge/Amazon_AWS-232F3E?logo=amazon-aws&logoColor=FF9900
[aws-url]: https://aws.amazon.com/
[aws-cloudwatch]: https://img.shields.io/badge/amazon_cloudwatch-232F3E?logo=amazoncloudwatch&logoColor=FF4F8B
[cdk]: https://img.shields.io/badge/AWS_Cloud_Development_Kit-232F3E?logo=data:image/png;base64,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
[python]: https://img.shields.io/badge/Python-232F3E?logo=python&logoColor=14354C
[AWSPrivateLink]: https://img.shields.io/badge/AWS_PrivateLink-232F3E?logo=data:image/png;base64,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