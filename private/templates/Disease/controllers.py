# -*- coding: utf-8 -*-

from gluon import *
from s3 import S3CustomController

TEMPLATE = "Disease"

# =============================================================================
class index(S3CustomController):
    """ Custom Home Page """

    def __call__(self):

        output = {}

        T = current.T
        request = current.request
        response = current.response
        s3 = response.s3

        # Check logged in and permissions
        auth = current.auth
        settings = current.deployment_settings
        roles = current.session.s3.roles
        system_roles = auth.get_system_roles()
        AUTHENTICATED = system_roles.AUTHENTICATED

        if settings.has_module("cms"):
            s3db = current.s3db
            table = s3db.cms_post
            ltable = s3db.cms_post_module
            query = (ltable.module == "default") & \
                    ((ltable.resource == None) | (ltable.resource == "index")) & \
                    (ltable.post_id == table.id) & \
                    (table.deleted != True)
            item = current.db(query).select(table.body,
                                            limitby=(0, 1)).first()
            if item:
                item = DIV(XML(item.body))
            else:
                item = ""
        else:
            item = ""

        # Login/Registration forms
        self_registration = current.deployment_settings.get_security_self_registration()
        registered = False
        login_form = None
        login_div = None
        register_form = None
        register_div = None
        
        if AUTHENTICATED not in roles:
            
            login_buttons = DIV(A(T("Login"),
                                  _id="show-login",
                                  _class="tiny secondary button"),
                                _id="login-buttons"
                                )
            script = '''
$('#show-intro').click(function(e){
 e.preventDefault()
 $('#intro').slideDown(400, function() {
   $('#login_box').hide()
 });
})
$('#show-login').click(function(e){
 e.preventDefault()
 $('#login_form').show()
 $('#register_form').hide()
 $('#login_box').show()
 $('#intro').slideUp()
})'''
            s3.jquery_ready.append(script)
            
            # This user isn't yet logged-in
            if request.cookies.has_key("registered"):
                # This browser has logged-in before
                registered = True

            if self_registration is True:
                # Provide a Registration box on front page
                login_buttons.append(A(T("Register"),
                                       _id="show-register",
                                       _class="tiny secondary button",
                                       # @ToDo: Move to CSS
                                       _style="margin-left:5px"))
                script = '''
$('#show-register').click(function(e){
 e.preventDefault()
 $('#login_form').hide()
 $('#register_form').show()
 $('#login_box').show()
 $('#intro').slideUp()
})'''
                s3.jquery_ready.append(script)

                register_form = auth.register()
                register_div = DIV(H3(T("Register")),
                                   P(XML(T("If you would like to help, then please %(sign_up_now)s") % \
                                            dict(sign_up_now=B(T("sign-up now"))))))

                register_script = '''
$('#register-btn').click(function(e){
 e.preventDefault()
 $('#register_form').show()
 $('#login_form').hide()
})
$('#login-btn').click(function(e){
 e.preventDefault()
 $('#register_form').hide()
 $('#login_form').show()
})'''
                s3.jquery_ready.append(register_script)
                
            # Provide a login box on front page
            auth.messages.submit_button = T("Login")
            login_form = auth.login(inline=True)
            login_div = DIV(H3(T("Login")),
                            P(XML(T("Registered users can %(login)s to access the system") % \
                                  dict(login=B(T("login"))))))

        else:
            login_buttons = ""

        output["item"] = item
        output["login_buttons"] = login_buttons
        output["self_registration"] = self_registration
        output["registered"] = registered
        output["login_div"] = login_div
        output["login_form"] = login_form
        output["register_div"] = register_div
        output["register_form"] = register_form

        self._view(TEMPLATE, "index.html")
        return output

# END =========================================================================