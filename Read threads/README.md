# Read threads

The experiment serves to display how to make an IP read thread that can run in a thread.

This thread is started by the user, and can be stopped by either the client/server disconnecting on the other side or the user asking for a stop (or the instance being deleted)

## Conclusion

Using ``select.select`` works very well using a socket and a socketpair as a stop flag. This solution should also work on Windows
