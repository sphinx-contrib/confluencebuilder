jira
----

.. single jira issue; no explicit server

.. jira_issue:: TEST-123

.. jira search; multiple options with server mapping

.. jira:: project = "TEST"
    :columns: key,summary,updated,status,resolution
    :count: false
    :maximum-issues: 5
    :server: test-jira-server

.. single jira issue; with explicit server override

.. jira_issue:: TEST-1
    :server-id: 00000000-0000-9876-0000-000000000000
    :server-name: overwritten-server-name
