"""
Chat API integration tests.

These are INTEGRATION tests (also called controller tests in some teams).
Unlike frontend tests which mock the API, these hit REAL endpoints against
a temporary test database that Django creates and destroys automatically.

Each test class has a setUp() method that runs before EVERY test — creating
fresh users, tokens, and data — so tests are fully isolated from each other.
One test can never break another.

In a professional team, these would run in CI/CD on every pull request.
If any test fails, the PR cannot be merged.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from accounts.models import User
from courses.models import Course, Enrollment
from .models import ChatConversation, ChatMessage


class ConversationCreateTests(TestCase):
    """Test creating new chat conversations via POST /api/chat/conversations/.

    When a user creates a conversation, the API should:
    1. Create the conversation record in the database
    2. Automatically add a welcome message from the assistant
    3. Return 201 Created with the conversation data
    """

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.token = Token.objects.create(user=self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_create_conversation(self):
        """Authenticated user can create a new conversation."""
        response = self.client.post('/api/chat/conversations/', {
            'title': 'My First Chat',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'My First Chat')
        # The conversation should exist in the database
        self.assertTrue(ChatConversation.objects.filter(title='My First Chat').exists())

    def test_create_conversation_includes_welcome_message(self):
        """New conversations should auto-include an assistant welcome message.

        This is important UX — the user sees a greeting immediately,
        so the chat doesn't feel empty.
        """
        response = self.client.post('/api/chat/conversations/', {
            'title': 'Welcome Test',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that one assistant message was auto-created
        conversation = ChatConversation.objects.get(title='Welcome Test')
        messages = conversation.messages.all()
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().role, 'assistant')
        self.assertIn('LearnHub assistant', messages.first().content)

    def test_create_conversation_unauthenticated(self):
        """Unauthenticated users should NOT be able to create conversations.

        This is a SECURITY test — it verifies that the IsAuthenticated
        permission class is correctly applied to the view.
        """
        client = APIClient()  # Fresh client with no credentials
        response = client.post('/api/chat/conversations/', {
            'title': 'Sneaky Chat',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Nothing should have been created in the database
        self.assertFalse(ChatConversation.objects.filter(title='Sneaky Chat').exists())


class ConversationListTests(TestCase):
    """Test listing conversations via GET /api/chat/conversations/.

    CRITICAL SECURITY RULE: Users should only see THEIR OWN conversations.
    A student should never see another student's private chat history.
    This is called "object-level permission" or "data isolation".
    """

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='alice', email='alice@example.com',
            password='testpass123', role='student',
        )
        self.user2 = User.objects.create_user(
            username='bob', email='bob@example.com',
            password='testpass123', role='student',
        )
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

        # Create conversations for each user
        self.convo1 = ChatConversation.objects.create(user=self.user1, title='Alice Chat')
        self.convo2 = ChatConversation.objects.create(user=self.user2, title='Bob Chat')

    def test_list_own_conversations_only(self):
        """Users should only see their own conversations — not other users'.

        This is the most important security test for chat. If this fails,
        it means users can read each other's private messages.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get('/api/chat/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        # Alice should see 1 conversation (her own), not Bob's
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Alice Chat')

    def test_list_conversations_unauthenticated(self):
        """Unauthenticated requests should be rejected."""
        client = APIClient()
        response = client.get('/api/chat/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConversationDetailTests(TestCase):
    """Test retrieving and deleting individual conversations.

    In a real app, these tests catch bugs like:
    - Users accessing other people's conversations via direct URL
    - Delete not actually removing messages (orphaned data)
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com',
            password='testpass123', role='student',
        )
        self.token = Token.objects.create(user=self.user)
        self.other_token = Token.objects.create(user=self.other_user)

        self.conversation = ChatConversation.objects.create(
            user=self.user, title='My Private Chat',
        )
        ChatMessage.objects.create(
            conversation=self.conversation, role='assistant', content='Welcome!',
        )

    def test_retrieve_own_conversation(self):
        """User can view their own conversation with all messages."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/chat/conversations/{self.conversation.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'My Private Chat')

    def test_cannot_retrieve_other_users_conversation(self):
        """User should NOT be able to access another user's conversation.

        This prevents a common security vulnerability where an attacker
        guesses conversation IDs to read other people's messages.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.other_token.key}')
        response = self.client.get(f'/api/chat/conversations/{self.conversation.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_conversation(self):
        """User can delete their own conversation and all its messages."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.delete(f'/api/chat/conversations/{self.conversation.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Conversation and its messages should be gone from the database
        self.assertFalse(ChatConversation.objects.filter(id=self.conversation.id).exists())
        self.assertFalse(ChatMessage.objects.filter(conversation=self.conversation).exists())


class MessageCreateTests(TestCase):
    """Test sending messages via POST /api/chat/conversations/<id>/messages/.

    When a user sends a message, the API should:
    1. Save the user's message
    2. Auto-generate a bot response (rule-based for now)
    3. Return BOTH messages in the response
    4. Auto-title the conversation from the first user message
    """

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student', email='student@example.com',
            password='testpass123', role='student',
        )
        self.token = Token.objects.create(user=self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.conversation = ChatConversation.objects.create(
            user=self.student, title='New Conversation',
        )

    def test_send_message_creates_user_and_assistant_messages(self):
        """Sending a message should create TWO records: user + bot response.

        This is the core chat flow — the user sends a message and gets
        an instant automated reply. Both are persisted to the database.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'Hello!'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Response should contain both messages
        self.assertIn('user_message', response.data)
        self.assertIn('assistant_message', response.data)
        self.assertEqual(response.data['user_message']['role'], 'user')
        self.assertEqual(response.data['assistant_message']['role'], 'assistant')

    def test_send_message_auto_titles_conversation(self):
        """The first user message should become the conversation title.

        This is a UX feature — instead of "New Conversation", the sidebar
        shows what the user actually asked about.
        """
        self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'How do I enrol in a course?'},
        )
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'How do I enrol in a course?')

    def test_send_empty_message_rejected(self):
        """Empty messages should be rejected with 400 Bad Request.

        This is INPUT VALIDATION — we don't want blank messages cluttering
        the database. The API checks for empty content before saving.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': ''},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_send_message_to_other_users_conversation_forbidden(self):
        """Users cannot send messages to conversations they don't own.

        This prevents a serious security issue — imagine if any user
        could inject messages into another user's chat history.
        """
        other_user = User.objects.create_user(
            username='other', email='other@example.com',
            password='testpass123', role='student',
        )
        other_convo = ChatConversation.objects.create(
            user=other_user, title='Private Chat',
        )
        # Try to send a message to someone else's conversation
        response = self.client.post(
            f'/api/chat/conversations/{other_convo.id}/messages/',
            {'content': 'I should not be here'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bot_responds_to_greeting(self):
        """Bot should recognise greetings and respond appropriately.

        This tests the rule-based chatbot logic — it pattern-matches
        keywords like "hello" and generates a relevant response.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'Hello there!'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bot_content = response.data['assistant_message']['content']
        # The greeting response should include the user's name
        self.assertIn('student', bot_content.lower())

    def test_bot_responds_to_course_query(self):
        """Bot should respond with course info when asked about courses.

        This tests that the chatbot can provide helpful, contextual
        responses about the platform's main feature.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'How do I find courses?'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bot_content = response.data['assistant_message']['content']
        # Should mention browsing courses
        self.assertIn('All Courses', bot_content)

    def test_bot_lists_actual_enrolled_courses_for_student(self):
        """When a student asks "what are my courses?", the bot must read
        their real enrolments out of the database — not a template.

        This is the data-driven branch of the chatbot (as opposed to the
        static keyword-matched branches), so the test creates a real
        Enrollment and asserts the course title shows up in the reply.
        """
        teacher = User.objects.create_user(
            username='teacher_bot', email='tb@example.com',
            password='testpass123', role='teacher',
        )
        course = Course.objects.create(
            title='Astrophysics 101', description='Stars and stuff',
            teacher=teacher,
        )
        Enrollment.objects.create(student=self.student, course=course)

        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'what are my enrolled courses?'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Astrophysics 101', response.data['assistant_message']['content'])

    def test_bot_blocks_student_asking_how_to_create_a_course(self):
        """When a student asks "how do I create a course?", the bot must
        explain that only teachers/admins can create courses — rather than
        sending them down the teacher flow.

        This tests the role-based branching inside the chatbot: the same
        keyword pattern produces different responses depending on the user.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'How do I create a new course?'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bot_content = response.data['assistant_message']['content'].lower()
        self.assertIn('teacher', bot_content)

    def test_bot_falls_back_for_unrecognised_input(self):
        """Messages that match no keyword pattern must still get a useful
        reply — the fallback that points the user at things the bot can do.

        Without this safety net, an unknown input would either crash or
        produce a confusing empty response.
        """
        response = self.client.post(
            f'/api/chat/conversations/{self.conversation.id}/messages/',
            {'content': 'asdjklhfaweqwerxyz'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bot_content = response.data['assistant_message']['content']
        # The fallback advertises the things the bot CAN handle.
        self.assertIn('Courses', bot_content)
        self.assertIn('Profile', bot_content)
