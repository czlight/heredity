import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    # used when we know nothing about a person's parents
    "gene": {
        2: 0.01, # 1% chance of having 2 copies of gene
        1: 0.03, # 3% chance of having 1 copy (and so on)
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        # whether a person has the trait depends on how many copies of gene they have
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability - gene mutates from having gene to not
    # having the gene, and vice versa
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    # people maps each person's name to another dictionary containing
    # info. about them including their name, their mother/father (if listed)
    # and whether they are observed to have the train in question (True/False)
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    print("joint_probability() function called!")
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    probabilities = {
        person: 0.0
        for person in people
    }

    totalProbabilities = 1.0
    print(people)

    for person in people:
        # reset probability for each new person in for loop

        # find probability of persons without parents
        if people[person]["father"] == None and people[person]["mother"] == None:
            if person in one_gene:
                # check probability that they have 1 gene
                print("check for parent", person, "with one gene and has trait")
                probabilities[person] = PROBS["gene"][1]

            elif person in two_genes:
                print("check for parent", person, "with two genes, has trait")
                probabilities[person] = PROBS["gene"][2]

            else:
                print("check for parent", person, "with no genes")
                # person is not in one or two gene set
                probabilities[person] = PROBS["gene"][0]

        print(probabilities)

        # find probability of persons with parents
        # both parents have two genes
        if people[person]["father"] in two_genes and people[person]["mother"] in two_genes:
            if person in two_genes:
                probabilities[person] = (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
            if person in one_gene:
                # inherit one gene
                probabilities[person] = 2 * (0.5 * (1 - PROBS["mutation"]))

            else:
                #inherit no genes
                probabilities[person] = PROBS["mutation"] * PROBS["mutation"]

        # one parent has two genes, the other has one gene
        elif (people[person]["father"] in two_genes and people[person]["mother"] in one_gene) or (people[person]["father"] in one_gene and people[person]["mother"] in two_genes):
            if person in two_genes:
                probabilities[person] = (1 - PROBS["mutation"]) * (.5 * (1 - PROBS["mutation"]) + (.5 * PROBS["mutation"]))
            if person in one_gene:
                #two scenarios: 1) inherit one gene from 1st parent and not the 2nd
                # 2) inherit one gene from 2nd parent and not the first; add these probabilities together
                probabilities[person] = (.5 * (1 - PROBS["mutation"]) * (.5 * PROBS["mutation"])) + (.5 * PROBS["mutation"]) * (.5 * (1 - PROBS["mutation"]))
            else:
                #inherit no genes
                probabilities[person] = (.5 * PROBS["mutation"]) * (.25 * PROBS["mutation"] + (.25 * (1 - PROBS["mutation"])))

        # one parent has two genes, the other has none
        elif (people[person]["father"] in two_genes and people[person]["mother"]  not in two_genes and people[person]["mother"] not in one_gene) \
            or (people[person]["mother"] in two_genes and (people[person]["father"]  not in two_genes and people[person]["father"] not in one_gene)):
                if person in two_genes:
                    probabilities[person] = (1 - PROBS["mutation"]) * PROBS["mutation"])
                if person in one_gene:
                    #one gene
                    probabilities[person] = (1- PROBS["mutation"] * (1 - PROBS["mutation"]) + (PROBS["mutation"] * (PROBS["mutation"])))
                else:
                    #person has no genes
                    probabilities[person] = .01 * .01


        # both parents have one_gene
        elif people[person]["father"] in one_gene and people[person]["mother"] in one_gene:
            if person in two_genes:
                probabilities[person] = (.5 * (1 - PROBS["mutation"])) * (.5 * (1 - PROBS["mutation"]))
            if person in one_gene:
                probabilities[person] = (.5 * .99 * .5 * .01) + (.5 * .01 * .5 * .99)
                # inherit one gene
            else:
                #inherit no genes; each parent has one gene out of two, so the probability of not inheriting the gene from each parent is 1/2: 1/2 *1/2 = 1/4
                probabilities[person] = (.5 * (1 - PROBS["mutation"])) * (.5 * (1 - PROBS["mutation"]))

        # one parent has one gene, the other parent has none
        elif (people[person]["father"] in one_gene and people[person]["mother"] not in two_genes and people[person]["mother"] not in one_gene) or \
            (people[person]["mother"] in one_gene and people[person]["father"] not in two_genes and people[person]["father"] not in one_gene):
            if person in two_genes:
                probabilities[person] =
            if person in one_gene:
                probabilities[person] =
                # inherit one gene
            else:
                #inherit no genes
                probabilities[person] =


        # neither parent has gene (will this run for people without parents? if it does it will )
        elif (people[person]["father"] not in one_gene and people[person]["father"] not in two_genes and people[person]["mother"] not in one_gene \
            and people[person]["mother"] not in two_genes):
            print("this person,", person, "should have parents")
            if person in two_genes:
                probabilities[person] =
            if person in one_gene:
                probabilities[person] =
                # inherit one gene
            else:
                #inherit no genes
                probabilities[person] =

        # check probability person has trait
        # two genes and has trait
        if person in two_genes and person in have_trait:
            probabilities[person] *= PROBS["trait"][2][True]
        elif person in two_genes and person not in have_trait:
            probabilities[person] *= PROBS["trait"][2][False]
        elif person in one_gene and person in have_trait:
            probabilities[person] *= PROBS["trait"][1][True]
        elif person in one_gene and person not in have_trait:
            probabilities[person] *= PROBS["trait"][1][False]
        elif (person not in one_gene and person not in two_genes) and person in have_trait:
            probabilities[person] *= PROBS["trait"][0][True]
        elif (person not in one_gene and person not in two_genes) and person not in have_trait:
            probabilities[person] *= PROBS["trait"][0][False]



        print("end of looP! for person", person, "probabilities are",probabilities)

        print("probabilities[person] is equal to", probabilities[person])
        totalProbabilities *= probabilities[person]
        print("totalProbabilities within llop:", totalProbabilities)

    print("totalProbabilities:", totalProbabilities)
    return totalProbabilities








def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
