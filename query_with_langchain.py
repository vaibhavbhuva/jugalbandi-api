import openai
from gpt_index import SimpleDirectoryReader
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain import PromptTemplate, OpenAI, LLMChain
from cloud_storage import *
import shutil
import array as arr


promptsInMemoryDomainQues = []
promptsInMemoryTechQues = []




def langchain_indexing(uuid_number):
    sources = SimpleDirectoryReader(uuid_number).load_data()
    source_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=4 * 1024, chunk_overlap=200)
    counter = 0
    for source in sources:
        for chunk in splitter.split_text(source.text):
            new_metadata = {"source": str(counter)}
            source_chunks.append(Document(page_content=chunk, metadata=new_metadata))
            counter += 1
    try:
        search_index = FAISS.from_documents(source_chunks, OpenAIEmbeddings())
        search_index.save_local("")
        error_message = None
        status_code = 200
    except openai.error.RateLimitError as e:
        error_message = f"OpenAI API request exceeded rate limit: {e}"
        status_code = 500
    except (openai.error.APIError, openai.error.ServiceUnavailableError):
        error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
        status_code = 503
    except Exception as e:
        error_message = str(e.__context__) + " and " + e.__str__()
        status_code = 500
    return error_message, status_code


def rephrased_question(user_query):
    template = """
    Write the same question as user input and make it more descriptive without adding new information and without making the facts incorrect.

    User: {question}
    Rephrased User input:"""
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=0), verbose=False)
    response = llm_chain.predict(question=user_query)
    return response.strip()


def querying_with_langchain(uuid_number, query):
    files_count = read_langchain_index_files(uuid_number)
    if files_count == 2:
        try:
            search_index = FAISS.load_local(uuid_number, OpenAIEmbeddings())
            chain = load_qa_with_sources_chain(
                OpenAI(temperature=0), chain_type="map_reduce"
            )
            paraphrased_query = rephrased_question(query)
            documents = search_index.similarity_search(paraphrased_query, k=5)
            answer = chain(
                {"input_documents": documents, "question": paraphrased_query}
            )
            answer_list = answer["output_text"].split("\nSOURCES:")
            final_answer = answer_list[0].strip()
            source_ids = answer_list[1]
            source_ids = source_ids.replace(" ", "")
            source_ids = source_ids.replace(".", "")
            source_ids = source_ids.split(",")
            final_source_text = ""
            for document in documents:
                if document.metadata["source"] in source_ids:
                    final_source_text += document.page_content + "\n\n"
            shutil.rmtree(uuid_number)
            return final_answer, final_source_text, paraphrased_query, None, 200
        except openai.error.RateLimitError as e:
            error_message = f"OpenAI API request exceeded rate limit: {e}"
            status_code = 500
        except (openai.error.APIError, openai.error.ServiceUnavailableError):
            error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
            status_code = 503
        except Exception as e:
            error_message = str(e.__context__) + " and " + e.__str__()
            status_code = 500
    else:
        error_message = "The UUID number is incorrect"
        status_code = 422
    return None, None, None, error_message, status_code


def querying_with_langchain_gpt4(uuid_number, query):
    if uuid_number.lower() == "storybot":
        try:
            system_rules = "I want you to act as an Indian story teller. You will come up with entertaining stories that are engaging, imaginative and captivating for children in India. It can be fairy tales, educational stories or any other type of stories which has the potential to capture children’s attention and imagination. A story should not be more than 200 words. The audience for the stories do not speak English natively. So use very simple English with short and simple sentences, no complex or compound sentences. Extra points if the story ends with an unexpected twist."
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_rules},
                    {"role": "user", "content": query},
                ],
            )
            return res["choices"][0]["message"]["content"], "", "", None, 200
        except openai.error.RateLimitError as e:
            error_message = f"OpenAI API request exceeded rate limit: {e}"
            status_code = 500
        except (openai.error.APIError, openai.error.ServiceUnavailableError):
            error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
            status_code = 503
        except Exception as e:
            error_message = str(e.__context__) + " and " + e.__str__()
            status_code = 500
        return None, None, None, error_message, status_code
    else:
        files_count = read_langchain_index_files(uuid_number)
        if files_count == 2:
            try:
                search_index = FAISS.load_local(uuid_number, OpenAIEmbeddings())
                documents = search_index.similarity_search(query, k=5)
                contexts = [document.page_content for document in documents]
                augmented_query = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n" + query
                system_rules = "You are a helpful assistant who helps with answering questions based on the provided information. If the information cannot be found in the text provided, you admit that I don't know"

                res = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_rules},
                        {"role": "user", "content": augmented_query},
                    ],
                )
                return res["choices"][0]["message"]["content"], "", "", None, 200

            except openai.error.RateLimitError as e:
                error_message = f"OpenAI API request exceeded rate limit: {e}"
                status_code = 500
            except (openai.error.APIError, openai.error.ServiceUnavailableError):
                error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
                status_code = 503
            except Exception as e:
                error_message = str(e.__context__) + " and " + e.__str__()
                status_code = 500
        else:
            error_message = "The UUID number is incorrect"
            status_code = 422
        return None, None, None, error_message, status_code

def querying_with_langchain_gpt4_streaming(uuid_number, query):
    files_count = read_langchain_index_files(uuid_number)
    if files_count == 2:
        try:
            search_index = FAISS.load_local(uuid_number, OpenAIEmbeddings())
            documents = search_index.similarity_search(query, k=5)
            contexts = [document.page_content for document in documents]
            augmented_query = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n" + query

            system_rules = "You are a helpful assistant who helps with answering questions based on the provided information. If the information cannot be found in the text provided, you admit that I don't know"

            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {"role": "system", "content": system_rules},
                    {"role": "user", "content": augmented_query}
                ],
                stream=True
            )

            # Define a generator function to yield each chunk of the response
            async def generate_messages():
                for chunk in response:
                    print(chunk)
                    # chunk_message = chunk['choices'][0]['delta']['content']
                    # chunk_message = chunk["choices"][0].get("delta", {}).get("content", '')
                    chunk_message = chunk["choices"][0].get("delta", {}).get("content", '')
                    yield chunk_message

            # Return a StreamingResponse with the generated messages
            return EventSourceResponse(generate_messages(), headers={"Content-Type":"text/plain"})
            # application/json

        except openai.error.RateLimitError as e:
            error_message = f"OpenAI API request exceeded rate limit: {e}"
            status_code = 500
            logger.exception("RateLimitError occurred: %s", e)
        except (openai.error.APIError, openai.error.ServiceUnavailableError):
            error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
            status_code = 503
            logger.exception("APIError or ServiceUnavailableError occurred")
        except Exception as e:
            error_message = str(e.__context__) + " and " + e.__str__()
            status_code = 500
            logger.exception("An exception occurred: %s", e)
    else:
        error_message = "The UUID number is incorrect"
        status_code = 422

    # return None, None, None, error_message, status_codewss
    # If there's an error, return a plain text response with the error message
    return Response(content=error_message, media_type="text/plain", status_code=status_code)

def querying_with_langchain_gpt4_mcq(uuid_number, query, doCache):
    if uuid_number.lower() == "tech":
        try:

            system_rules = getSystemRulesForTechQuestions()
            userContent = {"role": "user", "content": query}
            systemContent = {"role": "system", "content": system_rules}
            
            
            prompts = getPromptsForGCP(doCache, query, system_rules)
                
            if doCache:
                promptsInMemoryTechQues.extend(prompts)
            #     print("====================================================")
            #     print(promptsInMemoryTechQues)
            # else:
            #     print("777777777777777777777777777777777777777777777777777")
            #     print(prompts)
            
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages = promptsInMemoryTechQues if doCache else prompts,
            )

            respMsg = res["choices"][0]["message"]["content"]
            if doCache:
                promptsInMemoryTechQues.append({"role":"assistant", "content":respMsg});
            return respMsg, "", "", None, 200
        except openai.error.RateLimitError as e:
            error_message = f"OpenAI API request exceeded rate limit: {e}"
            status_code = 500
        except (openai.error.APIError, openai.error.ServiceUnavailableError):
            error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
            status_code = 503
        except Exception as e:
            error_message = str(e.__context__) + " and " + e.__str__()
            status_code = 500
        return None, None, None, error_message, status_code
    else:
        files_count = read_langchain_index_files(uuid_number)
        if files_count == 2:
            try:
                search_index = FAISS.load_local(uuid_number, OpenAIEmbeddings())
                documents = search_index.similarity_search(query, k=5)
                contexts = [document.page_content for document in documents]

                system_rules = getSystemRulesForDomainSpecificQuestions()
                context = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n"
                system_rules = system_rules.format(Context=context)

                prompts = getPromptsForGCP(doCache, query, system_rules)
                
                if doCache:
                    promptsInMemoryDomainQues.extend(prompts)
                    print("====================================================")
                    print(promptsInMemoryDomainQues)
                else:
                    print("==7777777777777777777===")
                    print(prompts)
                    

                res = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages = promptsInMemoryDomainQues if doCache else prompts,
                )

                respMsg = res["choices"][0]["message"]["content"]
                if doCache:
                    promptsInMemoryDomainQues.append({"role":"assistant", "content":respMsg})
                return respMsg, "", "", None, 200

            except openai.error.RateLimitError as e:
                error_message = f"OpenAI API request exceeded rate limit: {e}"
                status_code = 500
            except (openai.error.APIError, openai.error.ServiceUnavailableError):
                error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
                status_code = 503
            except Exception as e:
                error_message = str(e.__context__) + " and " + e.__str__()
                status_code = 500
        else:
            error_message = "The UUID number is incorrect"
            status_code = 422
        return None, None, None, error_message, status_code



def querying_with_langchain_gpt4_sajesh(uuid_number, query):
    if uuid_number.lower() == "storybot":
        try:
            system_rules = "I want you to act as an Indian story teller. You will come up with entertaining stories that are engaging, imaginative and captivating for children in India. It can be fairy tales, educational stories or any other type of stories which has the potential to capture children's attention and imagination. A story should not be more than 200 words. The audience for the stories do not speak English natively. So use very simple English with short and simple sentences, no complex or compound sentences. Extra points if the story ends with an unexpected twist."
            res = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_rules},
                    {"role": "user", "content": query},
                ],
            )
            return res["choices"][0]["message"]["content"], "", "", None, 200
        except openai.error.RateLimitError as e:
            error_message = f"OpenAI API request exceeded rate limit: {e}"
            status_code = 500
        except (openai.error.APIError, openai.error.ServiceUnavailableError):
            error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
            status_code = 503
        except Exception as e:
            error_message = str(e.__context__) + " and " + e.__str__()
            status_code = 500
        return None, None, None, error_message, status_code
    else:
        files_count = read_langchain_index_files(uuid_number)
        if files_count == 2:
            try:
                search_index = FAISS.load_local(uuid_number, OpenAIEmbeddings())
                documents = search_index.similarity_search(query, k=5)
                contexts = [document.page_content for document in documents]

                print("=================================================")

                for context in contexts:
                    print(context)

                print("=================================================")

                # This is for generating the technology questions - starts
                # TODO uncomment this for no-domain questions
                # system_rules = getSystemRulesForTechQuestions()
            # This is for generating the technology questions - ends

                # This is for generating the domain specific questions - starts
                # TODO uncomment this for domain specific questions
                system_rules = getSystemRulesForDomainSpecificQuestions()
                context = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n"
                system_rules = system_rules.format(Context=context)
                # print(system_rules)
                # This is for generating the domain specific questions - ends

                res = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {"role": "system", "content": system_rules},
                        {"role": "user", "content": query},
                    ],
                )

                # Split the CSV data into lines
                print(res["choices"][0]["message"]["content"])
                csv_lines = res["choices"][0]["message"]["content"].strip().split('\n')

                # Extract the header and remove it from the lines
                header = [column.strip('"') for column in csv_lines[0].split(',')]
                csv_lines = csv_lines[1:]

                # Create a list to hold the JSON objects
                json_list = []

                # Convert each line to a JSON object
                for line in csv_lines:
                    row = next(csv.reader([line], delimiter=',', quotechar='"'))
                    if len(header) == len(row):
                        json_object = {header[i]: row[i] for i in range(len(header))}
                        json_list.append(json_object)
                    else:
                        print(f"Skipping line: {line}. The number of columns does not match the header.")

                # Convert the list of JSON objects to a JSON string
                json_data = json.dumps(json_list, indent=4)

                # Print the JSON data
                print(json_data)

                return json_data, "", "", None, 200

            except openai.error.RateLimitError as e:
                error_message = f"OpenAI API request exceeded rate limit: {e}"
                status_code = 500
            except (openai.error.APIError, openai.error.ServiceUnavailableError):
                error_message = "Server is overloaded or unable to answer your request at the moment. Please try again later"
                status_code = 503
            except Exception as e:
                error_message = str(e.__context__) + " and " + e.__str__()
                status_code = 500
        else:
            error_message = "The UUID number is incorrect"
            status_code = 422
        return None, None, None, error_message, status_code


def getSystemRulesForTechQuestions():
    system_rules = """
                    You are a technology expert tasked with creating multiple-choice questions for a question bank. Your goal is to provide the question, options, and correct answer. Make sure that questions are not repeated.
    
                    Please generate the questions and encode the responses in CSV format. Use the following headers in lowercase with spaces replaced by underscores: question, option_a, option_b, option_c, option_d, correct_answer. Additionally, replace any commas in the CSV data with a dollar symbol ($). The output should be comma-separated.
                    
                    When generating the questions, list the options without prefixing them with option names like A, B, C, or D. However, specify the correct answer in the "correct_answer" column using the corresponding option letter.
                    
                    Example:
                    Question,Option_A,Option_B,Option_C,Option_D,Correct_Answer
                    What is the purpose of the sleep() method in Java?,To terminate a thread,To start a new thread,To pause the execution of a thread for a specific amount of time,To increase the priority of a thread,C
                    
                    Please generate the questions accordingly and provide the encoded CSV data.
                """
    return system_rules

def getSystemRulesForDomainSpecificQuestions():
    system_rules = """
                    You are a domain expert tasked with creating multiple-choice questions for a question bank. Your goal is to provide the question, options, and correct answer. Make sure that questions are not repeated.
                    
                    Given the following context:
                    
                    "{Context}"
                    
                    Please generate the questions and encode the responses in CSV format. Use the following headers in lowercase with spaces replaced by underscores: question, option_a, option_b, option_c, option_d, correct_answer. Additionally, replace any commas in the CSV data with a dollar symbol ($). The output should be properly formatted and comma-separated.
                    
                    Example:
                    Question,Option_A,Option_B,Option_C,Option_D,Correct_Answer
                    "What is the purpose of the sleep() method in Java?","To terminate a thread","To start a new thread","To pause the execution of a thread for a specific amount of time","To increase the priority of a thread","C"
                    
                    Please generate the questions accordingly and provide the encoded CSV data.
                """

    return system_rules


# def setSystemRules(promptType, contexts):
#     if promptType == "getSystemRulesForDomainSpecificQuestions":
#         system_rules = getSystemRulesForDomainSpecificQuestions()
#         context = "\n\n---\n\n".join(contexts) + "\n\n-----\n\n"
#         system_rules = system_rules.format(Context=context)
#         return system_rules 
#     else:
#         system_rules = getSystemRulesForTechQuestions()
#         return system_rules 

def getPromptsForGCP(doCache, query, system_rules):
    prompts = []
    userContent = {"role": "user", "content": query}
    systemContent = {"role": "system", "content": system_rules}
    if doCache:
        if len(prompts) <= 0:
            prompts.append(systemContent)
            prompts.append(userContent)
        else:
            prompts.append(userContent)
        return prompts
    else:
        singlePrompt = [
            systemContent,
            userContent
        ]
        return singlePrompt


