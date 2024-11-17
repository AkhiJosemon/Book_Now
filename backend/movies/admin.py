from django.contrib import admin
from .models import Movie, Theater, ShowTime ,Booking

# Inline for ShowTime in Movie Admin
class ShowTimeInline(admin.TabularInline):
    model = ShowTime
    extra = 1  # Default empty row to add more showtimes

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict theater choices based on the selected movie."""
        if db_field.name == "theater":
            # Get the movie being edited from the request
            movie_id = request.resolver_match.kwargs.get('object_id')
            if movie_id:
                movie = Movie.objects.get(id=movie_id)
                # Only show theaters associated with the selected movie
                kwargs['queryset'] = movie.theaters.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Admin for the Theater model
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Admin for Movie Model with ShowTime Inline
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'director', 'display_cast', 'display_theaters', 'language', 'category')
    search_fields = ('name', 'director', 'cast')
    list_filter = ('language', 'category', 'theaters')  # Filters for language, category, and theater
    filter_horizontal = ('theaters',)  # Enables a better UI for ManyToManyField selection
    inlines = [ShowTimeInline]  # Adding ShowTimes inline to MovieAdmin

    def display_cast(self, obj):
        """Display the first three cast members as a comma-separated list."""
        cast_list = obj.get_cast_list()
        return ", ".join(cast_list[:3]) + ("..." if len(cast_list) > 3 else "")

    display_cast.short_description = 'Cast'

    def display_theaters(self, obj):
        """Display associated theaters as a comma-separated list."""
        return ", ".join(obj.get_theater_names())

    display_theaters.short_description = 'Theaters'

# Registering the models with their respective admin classes
admin.site.register(Theater, TheaterAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Booking)
