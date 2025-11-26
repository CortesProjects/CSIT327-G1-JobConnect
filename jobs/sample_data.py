"""
Sample data helper removed.

Jobs should be created and read from the database (via fixtures, the admin,
or migration scripts). The previous `load_sample_jobs` helper was kept for
development but contained fields (like `industry`) that no longer match the
`Job` model. To avoid confusion the helper has been removed.

If you previously used this to populate local data, use Django fixtures or
create Job instances via the admin or a short management command that matches
the current `Job` model fields.
"""
