"""Current admission restrictions; archival records remain readable.

The project's adult boundary is 18. PMC10743793 Table 2 reports ages 16–85.
A title saying adult does not establish an exclusively >=18 aggregate.
"""


def population_restriction(metadata):
    identifiers = " ".join(
        str(metadata.get(k, "")) for k in ("id", "source_url", "doi", "pmcid", "raw_sha256")
    )
    if any(
        token in identifiers.lower()
        for token in (
            "adult-aom-inner-ear-2023",
            "pmc10743793",
            "10.3390/jcm12247590",
            "ca5393254b98b9cd0b0ec7bcd042a4f19cc8cfcc1a991a82d7abbcdf1753e817",
        )
    ):
        return "mixed_16_85_requires_adult_subgroup_review"
    return None
