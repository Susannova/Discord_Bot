# Style
 * In general, follow [PEP8](https://www.python.org/dev/peps/pep-0008/)
 * Create explicit and descriptive commit messages
 * Maximum Line Length: 119
 * Use [black code formatter](https://github.com/psf/black)
 * Imports are sorted in three blocks:
   * Standard library
   * 3rd party
   * Local
 * Always use Function Annotations ([PEP 484](https://www.python.org/dev/peps/pep-0484/))
 * Docstrings
    * End sentences with dots
    * First Character of each sentence is capitalized.
    * Referenced variables have to be in quotes: ``
    * Single Line: See [here](https://github.com/Susannova/Discord_Bot/blob/c9e2d0e9556c510671dc9af9b35655a037969bd4/cogs/cog_config.py#L47)
    * Multiple Lines: See [here](https://github.com/Susannova/Discord_Bot/blob/c9e2d0e9556c510671dc9af9b35655a037969bd4/cogs/cog_config.py#L70-L75)
    * Grammar: Present Tense, Imperative Mood
    * Spacing: 
      * No extra line between Docstring and method/function
      * One extra line after Class Docstrings
 

# Feature Development Process
  1. Refactors/Linting/Function annotations/Style changes can be pushed to the "Beta" branch directly
  2. New Features:
      * Each new feature requires its own branch
      * Create a pull request of your branch into the "Beta" branch (Don't delete the branch)
      * Features with accepeted pull requests will be tested in the "Beta" branch on the live bot
      * If the feature is stable, the feature branch will be merged into master
