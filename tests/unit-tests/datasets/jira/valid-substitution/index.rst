:orphan:

jira
----

.. substitution for single jira issue

.. |TEST-1| jira_issue:: TEST-1

|TEST-1|

.. substitution for jira search

.. |MY_JIRA_LIST| jira:: project = "TESTPRJ"
    :columns: key,summary,status,resolution
    :count: false
    :maximum-issues: 8

|MY_JIRA_LIST|

.. substitution for jira role

.. |TEST-2| replace:: :jira:`TEST-2`

|TEST-2|
