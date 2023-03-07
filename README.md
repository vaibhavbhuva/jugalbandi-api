## Jugalbandi API

Juglabnadi APIs is a system of APIs that allows users to build Q&A style applications on their private and public datasets. The system creates Open API 3.0 specification endpoints using FastAPI.

---

## How to use?

To use Jugalbandi APIs you can follow below steps to get you started:

1.  Visit [https://api.jugalbandi.ai/docs](https://api.jugalbandi.ai/docs). 
2.  Scroll to `upload-file` endpoint to upload the document
3.  Once you have uploaded file(s) you should have received a `uuid` number for that document set. Please keep this number handy as it will be required for you to query the document set.
4.  Now that you have the `uuid`  you should scroll up to select the query endpoint you want to use. Currently there are three different implementations we support i.e. `query_using_gptindex`, `query_with_langchain` (recommended), `query_using_voice` (recommended for voice interfaces). While you can use any of the query systems, we are constantly refining our langchain implementation.
5.  Pass on the `uuid` number and do the query.

## Feature request and contribution

*   We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
*   You should visit our project board to see what is it that we are prioritizing.
