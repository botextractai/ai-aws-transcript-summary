# Transcribe and summarize an audio file with a Large Language Model (LLM) using Amazon Bedrock

The [Amazon Web Service (AWS) Transcribe](https://aws.amazon.com/pm/transcribe/) service automatically converts speech to text. The speech can be in audio or video files. The AWS Transcribe service is often used to convert recorded customer conversations, such as support calls, to text for further processing. It has many other use cases, such as converting meeting recordings to text, or to extract information from videos or movies.

The [AWS Bedrock](https://aws.amazon.com/bedrock/) service offers a choice of Large Language Models (LLMs) via a single API.

This project converts a recorded audio conversion from the "dialog.mp3" file to text. It then uses a LLM to summarize the conversation in a detailed JSON format for further processing. The output format of the LLM is defined in a prompt template that is processed by the [Jinja template engine](https://palletsprojects.com/p/jinja/).

For this project, you need an AWS account. If you just want to try out AWS, then you can get a [AWS Free Tier account](https://aws.amazon.com/free/) for a year. This gives you a fair amount of free AWS usage for a whole year.

Once you are logged in to your AWS account, you need to create an access key in the "Security credentials" section by clicking on "Create access key". Access keys have two parts, the "Key ID" and the "Secret access key". You need to insert both parts in the "ai-aws-transcript-summary.py" script. The "Secret access key" is available only at the time when you create it. If you lose your "Secret access key", you must delete the access key and create a new one.

Amazon services run in dedicated regions. You can run services in a region of your choice. The project uses the "us-west-2" region, which is in Oregon (USA). If you want to use another region, then you need to change the "ai-aws-transcript-summary.py" script accordingly.

This project works with the Amazon [Titan Text G1 - Express](https://aws.amazon.com/bedrock/titan/) LLM. You must request access to the "Titan Text G1 - Express" model in the AWS Bedrock service. This is a very simple process and access to the model is granted instantly.

AWS Transcribe can only transcribe files to and from AWS S3 (Simple Storage Service) buckets. You therefore need to create a S3 bucket and insert the name of the S3 bucket in the "ai-aws-transcript-summary.py" script.

The program code has two phases. The first phase converts the audio file using AWS Transcribe. The transcription job specifies that it should identify two speakers. After the transcription job is completed, the output of the transcription gets formatted and saved in a file called "transcription-job-YOUR-UUID.txt" in the S3 bucket. You will notice that the transcription is reasonably good, but not perfect. The content of the text file will look like this:

```
spk_0: Hi, is this the Crystal Heights Hotel in Singapore?
spk_1: Yes, it is. Good afternoon. How may I assist you today?
spk_0: Fantastic, good afternoon. I was looking to book a room for my 10th wedding anniversary. Ive heard your hotel offers exceptional views and services. Could you tell me more?
spk_1: Absolutely, Alex and congratulations on your upcoming anniversary. Thats a significant milestone and wed be honored to make it a special occasion for you. We have several room types that offer stunning views of the city skyline and the fictional Sapphire Bay. Our special diamond suite even comes with exclusive access to the moonlit pool and star deck. We also have in house spa services, world class dining options and a shopping arcade.
spk_0: That sounds heavenly. I think my spouse would love the moonlit pool. Can you help me make a reservation for one of your diamond suites with a sapphire bay view?
spk_1: Of course. May I know the dates you planning to visit?
spk_0: Sure. It would be from October 10th to 17th.
spk_1: Excellent. Let me check the availability. Ah It looks like we have a diamond suite available for those dates. Would you like to proceed with the reservation?
spk_0: Definitely. Whats included in the package?
spk_1: Wonderful. The package includes breakfast, complimentary access to the moonlit pool and star deck. A one time spa treatment for two and a special romantic dinner at our cloud nine restaurant.
spk_0: You making it impossible to resist. Lets go ahead with the booking.
spk_1: Great. I'll need some personal information for the reservation. Can I get your full name, contact details and a credit card for the preauthorizations?
spk_0: Certainly. My full name is Alexander Thompson. My contact number is 12345678910. And the credit card is, wait, did you say pre authorization? How much would that be?
spk_1: Ah, I should have mentioned that earlier. My apologies. A pre authorization. A mt of $1000 will be held on your card which would be released upon checkout
spk_0: $1000. That seems a bit excessive. Don't you think
spk_1: I understand your concern, Alex. The pre authorization is a standard procedure to cover any incidental expenses you may incur during your stay. However, I assure you its only a hold and not an actual charge.
spk_0: Thats still a lot. Are there any additional charges that I should know about?
spk_1: Well, there is a 10% service charge and a 7% fantasy tax applied to the room rate.
spk_0: Mm. You know what its a special occasion. So lets go ahead.
spk_1: Thank you, Alex for understanding. Will ensure that your experience at Crystal Heights is well worth it.
```

The second phase reads the newly created transcription text file and uses the LLM to summarize the content. The LLM prompt gets generated by the Jinja engine using the template defined in the "prompt_template.txt" file. This prompt template instructs the LLM to respond with a summary that contains a one word sentiment analysis, and a list of issues, problems or causes of friction during the conversation. It also instructs the LLM to answer in JSON format.

The output from the LLM gets saved in in a file called "result-transcription-job-YOUR-UUID.json" in the S3 bucket. The output could be improved by tuning the prompt template. The content of the JSON file looks like this:

```
{
    "sentiment": "Positive",
    "issues": [
        {
            "topic": "Hotel services",
            "summary": "The hotel offers exceptional views and services."
        },
        {
            "topic": "Room booking",
            "summary": "The hotel has several room types that offer stunning views of the city skyline and the fictional Sapphire Bay."
        },
        {
            "topic": "Special occasion",
            "summary": "The hotel is honored to make it a special occasion for the couple's 10th wedding anniversary."
        },
        {
            "topic": "Diamond suite",
            "summary": "The special diamond suite comes with exclusive access to the moonlit pool and star deck."
        },
        {
            "topic": "In-house spa services",
            "summary": "The hotel has in-house spa services, world-class dining options, and a shopping arcade."
        },
        {
            "topic": "Reservation process",
            "summary": "The reservation process includes breakfast, complimentary access to the moonlit pool and star deck, a one-time spa treatment for two, and a special romantic dinner at the cloud nine restaurant."
        },
        {
            "topic": "Package details",
            "summary": "The package includes breakfast, complimentary access to the moonlit pool and star deck, a one-time spa treatment for two, and a special romantic dinner at the cloud nine restaurant."
        },
        {
            "topic": "Pre-authorization",
            "summary": "A pre-authorization of $1000 will be held on the couple's credit card, which will be released upon checkout."
        },
        {
            "topic": "Additional charges",
            "summary": "There is a 10% service charge and a 7% fantasy tax applied to the room rate."
        }
    ]
}
```
