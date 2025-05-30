# Generated by Django 4.2.11 on 2024-04-10 17:04

import business.utils.storage
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AbstractReport",
            fields=[
                (
                    "file_local_path",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("report_path", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="FirstLevelComment",
            fields=[
                (
                    "comment_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("text", models.TextField()),
                ("like_count", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Paper",
            fields=[
                (
                    "paper_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("authors", models.CharField(max_length=255)),
                ("abstract", models.TextField()),
                ("publication_date", models.DateField()),
                ("journal", models.CharField(max_length=255, null=True)),
                ("citation_count", models.IntegerField(default=0)),
                ("original_url", models.URLField()),
                ("read_count", models.IntegerField(default=0)),
                ("like_count", models.IntegerField(default=0)),
                ("collect_count", models.IntegerField(default=0)),
                ("comment_count", models.IntegerField(default=0)),
                ("download_count", models.IntegerField(default=0)),
                ("score", models.FloatField(default=0.0)),
                ("local_path", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "user_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("username", models.CharField(max_length=255)),
                ("password", models.CharField(max_length=255)),
                (
                    "avatar",
                    models.ImageField(
                        default="resource/uploads/users/avatars/default.jpg",
                        null=True,
                        storage=business.utils.storage.ImageStorage(),
                        upload_to="resource/uploads/users/avatars/",
                    ),
                ),
                ("registration_date", models.DateTimeField(auto_now_add=True)),
                (
                    "collected_papers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="collected_by_users",
                        to="business.paper",
                    ),
                ),
                (
                    "liked_papers",
                    models.ManyToManyField(
                        blank=True, related_name="liked_by_users", to="business.paper"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserDocument",
            fields=[
                (
                    "document_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("local_path", models.CharField(max_length=255)),
                ("upload_time", models.DateTimeField(auto_now_add=True)),
                ("format", models.CharField(max_length=50)),
                ("size", models.IntegerField()),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SummaryReport",
            fields=[
                (
                    "report_path",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SecondLevelComment",
            fields=[
                (
                    "comment_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("text", models.TextField()),
                ("like_count", models.IntegerField(default=0)),
                (
                    "lever1_comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="business.firstlevelcomment",
                    ),
                ),
                (
                    "liked_by_users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="liked_second_level_comments",
                        to="business.user",
                    ),
                ),
                (
                    "paper_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.paper"
                    ),
                ),
                (
                    "reply_comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="business.secondlevelcomment",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="firstlevelcomment",
            name="liked_by_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="liked_first_level_comments",
                to="business.user",
            ),
        ),
        migrations.AddField(
            model_name="firstlevelcomment",
            name="paper_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="business.paper"
            ),
        ),
        migrations.AddField(
            model_name="firstlevelcomment",
            name="user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="business.user"
            ),
        ),
        migrations.CreateModel(
            name="CommentReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comment_id", models.IntegerField()),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("content", models.CharField(max_length=255)),
                ("judgment", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaperScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "score",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10),
                        ]
                    ),
                ),
                (
                    "paper_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.paper"
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
            options={
                "unique_together": {("user_id", "paper_id")},
            },
        ),
        migrations.CreateModel(
            name="FileReading",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_local_path", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("conversation_path", models.CharField(max_length=255, unique=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="business.user"
                    ),
                ),
            ],
            options={
                "unique_together": {("user_id", "file_local_path")},
            },
        ),
    ]
