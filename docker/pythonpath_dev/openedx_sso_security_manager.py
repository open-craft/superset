import logging
from superset.security import SupersetSecurityManager
from superset.extensions import security_manager
from superset.utils.core import get_username
from superset.utils.memoized import memoized


class OpenEdxSsoSecurityManager(SupersetSecurityManager):

    def oauth_user_info(self, provider, response=None):
        logging.debug(f"Oauth2 provider: {provider}, response={response}.")
        if provider == 'openedxsso':
            me = self.appbuilder.sm.oauth_remotes[provider].get('api/user/v1/me').json()
            logging.debug("me: {0}".format(me))
            username = me['username']
            user_profile = self.appbuilder.sm.oauth_remotes[provider].get(f"api/user/v1/accounts/{username}").json()
            logging.debug("user_profile: {0}".format(user_profile))

            return {
                'name': user_profile['name'],
                'email': user_profile['email'],
                'id': user_profile['username'],
                'username': user_profile['username'],
                'first_name': '',
                'last_name': '',
                # FIXME: need to fetch this from an Open edX API too
                'role_keys': ["admin"],
            }


def can_view_courses():
    """
    Fetch the list of courses for the current user.
    """
    username = get_username()
    courses = _can_view_courses(username)
    courses_in = "(" + ",".join(courses) + ")"
    return courses_in


@memoized
def _can_view_courses(username, access="staff", next_url=None):
    """
    Returns the list of courses the current user has access to.
    """
    # TODO: global staff users have access to all courses, but:
    # a) we don't have an API that tells us if a user is a global staff/superuser, and
    # b) we shouldn't ever fetch the full list of courses.
    #
    # FIXME: what happens when the list of courses grows beyond what the query will handle?
    courses = []
    url = next_url or f"api/courses/v1/courses/?permissions={access}&username={username}"

    # FIXME: fails with "missing token".  bugger.
    response = security_manager.oauth_remotes["openedxsso"].get(url).json()

    for course in response.get('results', []):
        course_id = course.get('course_id')
        if course_id:
            courses.append(course_id)

    # Recurse to iterate over all the pages of results
    if response.get("next"):
        next_courses = _can_view_courses(username, next_url=response['next'])
        for course_id in next_courses:
            courses.append(course_id)

    # If you have staff access to one or more courses, you get to be an admin.
    logging.debug(f"Courses for {username}: {courses}")
    return courses
