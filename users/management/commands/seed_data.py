import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from projects.models import Project
from tasks.models import Task, Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with fake data for projects, tasks, and users.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Task.objects.all().delete()
            Comment.objects.all().delete()
            Project.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared successfully.'))

        fake = Faker()
        self.stdout.write(self.style.SUCCESS('Starting to seed the database...'))

        # --- 1. Create Users ---
        self.stdout.write('Creating users...')
        
        # Create Superuser if not exists
        if not User.objects.filter(email='admin@example.com').exists():
            admin_user = User.objects.create_superuser('admin@example.com', 'admin123')
            admin_user.first_name = "Admin"
            admin_user.last_name = "User"
            admin_user.profile.role = 'admin'
            admin_user.profile.save()
            admin_user.save()
        else:
            admin_user = User.objects.get(email='admin@example.com')

        managers = []
        for _ in range(3):
            email = fake.unique.email()
            user = User.objects.create_user(email, 'pass123', first_name=fake.first_name(), last_name=fake.last_name())
            user.profile.role = 'manager'
            user.profile.save()
            managers.append(user)

        developers = []
        for _ in range(10):
            email = fake.unique.email()
            user = User.objects.create_user(email, 'pass123', first_name=fake.first_name(), last_name=fake.last_name())
            user.profile.role = 'developer'
            user.profile.save()
            developers.append(user)

        clients = []
        for _ in range(5):
            email = fake.unique.email()
            user = User.objects.create_user(email, 'pass123', first_name=fake.first_name(), last_name=fake.last_name())
            user.profile.role = 'client'
            user.profile.save()
            clients.append(user)

        self.stdout.write(self.style.SUCCESS(f'{len(managers) + len(developers) + len(clients) + 1} users created.'))

        # --- 2. Create Projects ---
        self.stdout.write('Creating projects...')
        projects = []
        project_owners = [admin_user] + managers
        for i in range(15):
            owner = random.choice(project_owners)
            project = Project.objects.create(
                name=f"{fake.bs().title()} Project",
                description=fake.paragraph(nb_sentences=5),
                owner=owner,
            )
            projects.append(project)

            # Add members to the project
            project_devs = random.sample(developers, k=random.randint(2, 5))
            members_to_add = project_devs + [owner]
            if i % 3 == 0 and clients: # Add a client to some projects
                members_to_add.append(random.choice(clients))
            project.members.set(members_to_add)

        self.stdout.write(self.style.SUCCESS(f'{len(projects)} projects created.'))

        # --- 3. Create Tasks and Comments ---
        self.stdout.write('Creating tasks and comments...')
        tasks_list = []
        for project in projects:
            project_members = list(project.members.all())
            for _ in range(random.randint(5, 20)): # 5 to 20 tasks per project
                assignee = random.choice([m for m in project_members if m.profile.role in ['developer', 'manager']])
                due_date = fake.date_time_between(start_date='-30d', end_date='+60d', tzinfo=None).date()
                
                task = Task.objects.create(
                    title=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=3),
                    project=project,
                    assigned_to=assignee,
                    status=random.choice(['todo', 'in_progress', 'done']),
                    due_date=due_date,
                    recurrence=random.choice(['none', 'none', 'none', 'daily', 'weekly']) # 'none' is more frequent
                )
                tasks_list.append(task)

                # Create comments for the task
                for _ in range(random.randint(0, 8)):
                    commenter = random.choice(project_members)
                    Comment.objects.create(
                        content=fake.sentence(),
                        author=commenter,
                        task=task
                    )
        
        # Add some dependencies
        for task in tasks_list:
            if random.random() < 0.15: # 15% chance to have a dependency
                possible_deps = [t for t in tasks_list if t.project == task.project and t.id != task.id and not t.depends_on]
                if possible_deps:
                    task.depends_on = random.choice(possible_deps)
                    task.save()

        self.stdout.write(self.style.SUCCESS(f'{len(tasks_list)} tasks created with comments and dependencies.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.NOTICE('--- Sample Login Credentials ---'))
        self.stdout.write(self.style.NOTICE(f"Admin: admin@example.com / admin123"))
        if managers:
            self.stdout.write(self.style.NOTICE(f"Manager: {managers[0].email} / pass123"))
        if developers:
            self.stdout.write(self.style.NOTICE(f"Developer: {developers[0].email} / pass123"))
        if clients:
            self.stdout.write(self.style.NOTICE(f"Client: {clients[0].email} / pass123"))
        self.stdout.write(self.style.NOTICE('---------------------------------'))