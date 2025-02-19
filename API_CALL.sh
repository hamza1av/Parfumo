curl --http1.1 -x http://127.0.0.1:8080 -k -X POST "https://www.parfumo.de/action/_get_ratings_details.php" \
-H "Accept: */*" \
-H "Content-Type: application/x-www-form-urlencoded" \
-H "Cookie: PHPSESSID=h1ug0djf4v2603la1ai6t8ic1e; _ga=GA1.1.297718056.1739031516; _sp_su=false; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CQMgjEAQMgjEAAGABCENBbFsAP_gAAAAAAYgIzAB5C7cTWFhcHhXAaMAaIwc1xABJkAAAhKAAaABSBIAcIQEkiACMAyAAAACAAAAIABAAAAgAABAAQAAAIgAAAAEAAAEAAAIICAEAAERQgAACAAICAAAAQAIAAABAgEAi ACAQQKERFgAgIAgBAAAAIAgAIABAgMAAAAAAAAAAAAAAgAAgQAAAAAAAAACABAAAAeEgNAALAAqABwADwAIIAZABqADwAIgATAA3gB-AEJAIYAiQBHACaAGGAO6AfgB-gG0AUeAvMBkgDLgGsANzAgmEAEgAkACOAH8Ac4BKQCdgI9AXUAyEQABABIKAAgI9GAAQEejoDoACwAKgAcABBADIANQAeABEACYAF0AMQAbwA_QCGAIkATQAw4B-AH6ARYAjoBtAEXgJkAUeAvMBkkDLAMuAaaA1gBxYEARwBAAC4AJAAjgBQAD-AI6AcgBzgDuAIQASkAnYCPQExALqAZCA3MhAIAAWADUAMQAbwBHADuAJSAbQgAFAD_AOQA5wEegJiAiySgHgALAA4ADwAIgATAAxQCGAIkARwA_AEXgKPAXmAyQBrAEASQAcAC4ARwB3AHbAR6AmIBlhSAsAAsACoAHAAQQAyADQAHgARAAmABSADEAH6AQwBEwD8AP0AiwBHQDaAIvAXmAySBlgGXANYAgmUAJAAKAAuACQAI4AWwA2gCOgHIAc4A7gCUgF1ANeAdsBHoCYgFZANzAiyWgBAA1AHcWABAI9ATE.YAAAAAAAAAAA" \
-H "DNT: 1" \
-H "Origin: https://www.parfumo.de" \
-H "Referer: https://www.parfumo.de/Parfums/Viktor_Rolf/Spicebomb_Extreme" \
-H "Sec-CH-UA: \"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"" \
-H "Sec-CH-UA-Mobile: ?0" \
-H "Sec-CH-UA-Platform: \"macOS\"" \
-H "Sec-Fetch-Dest: empty" \
-H "Sec-Fetch-Mode: cors" \
-H "Sec-Fetch-Site: same-origin" \
-H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36" \
-H "X-Requested-With: XMLHttpRequest" \
-H "Host: www.parfumo.de" \
-H "Accept-Encoding: gzip, deflate, br" \
-H "Connection: keep-alive" \
--data-urlencode "type=scent" \
--data-urlencode "p_id=58361" \
--data-urlencode "dist=eyIwIjoxMiwiMTAiOjE0LCIyMCI6MTcsIjMwIjoxNywiNDAiOjQxLCI1MCI6NjgsIjYwIjoxNTQsIjcwIjo2NDcsIjgwIjoxNzY3LCI5MCI6MTY0OSwiMTAwIjo2NTl9" \
--data-urlencode "csrf_key=69f5e7a68ec2676603a4adf7baef0138" \
--data-urlencode "h=962bfc4721085a0f338bd4725bcf2e0c" \
-o response.br

# -H "Postman-Token: 9100e606-b869-46e3-95b1-67319a262d00" \
# -H "Content-Length: 774" \
# -H "Content-Type: multipart/form-data; boundary=--------------------------768301699983173237855751" \
