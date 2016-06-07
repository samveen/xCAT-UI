Design considerations
The design of this UI followed from the needs of an internal company project
that we were in the middle of. Hopefully, when there is more traction on this
project, the design will evolve to be more generalised and usable outside of my
particular set of use cases.

Auth
Auth piggybacks off PAM. In most infrastructure, auth is centralised and
utilizes PAM on the client side. Thus, instead of using an external service or
connection, we just use PAM directly.
