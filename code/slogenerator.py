from num2words import num2words
import yaml

def build_thresholds(level, number_of_thresholds_to_add):
  thresholds = list()
  count = 1
  while count <= number_of_thresholds_to_add:
    ordinal = num2words(count, to="ordinal_num")
    threshold = input(f"Please add your {ordinal} {level} threshold (eg. <=400 or <10%): ")
    thresholds.append(threshold)
    count += 1
  return thresholds

print("Starting Keptn SLO File Generator...")

#---
#spec_version: "1.0"
#comparison:
#  aggregate_function: "avg"
#  compare_with: "single_result"
#  include_result_with_score: "pass"
#  number_of_comparison_results: 1
#filter:
#objectives:
#  - sli: "response_time_p95"
#    displayName: "Response time P95"
#    key_sli: false
#    pass:             # pass if (relative change <= 10% AND absolute value is < 600ms)
#      - criteria:
#          - "<=+10%"  # relative values require a prefixed sign (plus or minus)
#          - "<600"    # absolute values only require a logical operator
#    warning:          # if the response time is below 800ms, the result should be a warning
#      - criteria:
#          - "<=800"
#    weight: 1
#total_score:
#  pass: "90%"
#  warning: "75%"

# Use sensible defaults according to Keptn docs
slo_definition = {
  "spec_version": "1.0",
  "comparison": {
    "aggregate_function": "avg",
    "compare_with": "single_result",
    "include_result_with_score": "pass",
    "number_of_comparison_results": 1
  },
  "filter": {},
  "objectives": [],
  "total_score": {
    "pass": "90%",
    "warning": "75%"
  }

}

# Build Objectives List
number_of_slis = None
while number_of_slis is None:
  number_of_slis = input("How many SLIs do you want to include? ")

  try:
    number_of_slis = int(number_of_slis)
  except:
    number_of_slis = None
    print('Got an invalid number of SLIs. Please use numbers. Try again...')

sli_list = list()
count = 1
while count <= number_of_slis:
  ordinal = num2words(count, to="ordinal_num")
  sli_name = input(f"Please enter the name of your {ordinal} SLI: ")
  sli_display_name = input(f"If you'd like to define a display name for {sli_name}, please enter it now. Otherwise, hit ENTER: ")
  if sli_display_name == "": sli_display_name = sli_name

  sli_weight = None
  while sli_weight is None:
    try:
      sli_weight = input(f"Add a custom weighting for {sli_name}? If not, hit enter (defaults to 1): ")
      if sli_weight == "": sli_weight = 1
      else: sli_weight = int(sli_weight)
    except:
      sli_weight = None
      print(f'Please enter a number for the weight of {sli_weight}. Try again...')
  
  key_sli = "false"
  key_sli = input(f"Set {sli_name} as a Key SLI? If not, hit enter (defaults to false): ")
  if key_sli == "": key_sli = "false"
  else:
    key_sli = "true"

  add_thresholds = input(f"Would you like to add pass / warning thresholds for {sli_name}? (y or n). If not, hit ENTER (defaults to no - informational only): ")

  # Set pass_thresholds and warning_thresholds to None in case user does not want to add thresholds
  # Then at least we can compare against None values later
  # If hte user does want to add thresholds, these lists will be built below
  pass_thresholds = None
  warning_thresholds = None
  if add_thresholds != "" and add_thresholds.lower() not in ["n","no"]:
    number_of_pass_thresholds_to_add = None
    while number_of_pass_thresholds_to_add is None:
      try:
        number_of_pass_thresholds_to_add = input(f"How many pass thresholds would you like to add to {sli_name}? ")
        number_of_pass_thresholds_to_add = int(number_of_pass_thresholds_to_add)
      except:
        number_of_pass_thresholds_to_add: None
        print(f"Please enter a number (not a string) for how many pass thresholds you'd like to add. Try again...")
    
    pass_thresholds = build_thresholds("pass", number_of_pass_thresholds_to_add)

    add_warning_thresholds = input(f"Pass thresholds added. Would you like to add warning thresholds for {sli_name}? (y or n). If not, hit ENTER (defaults to no): ")
    if add_warning_thresholds != "" and add_warning_thresholds.lower() not in ["n", "no"]:
      number_of_warning_thresholds_to_add = None
    while number_of_warning_thresholds_to_add is None:
      try:
        number_of_warning_thresholds_to_add = input(f"How many warning thresholds would you like to add to {sli_name}? ")
        number_of_warning_thresholds_to_add = int(number_of_warning_thresholds_to_add)
      except:
        number_of_warning_thresholds_to_add: None
        print(f"Please enter a number (not a string) for how many warning thresholds you'd like to add. Try again...")
    
    warning_thresholds = build_thresholds("pass", number_of_warning_thresholds_to_add)

  # Done gathering data for this SLI. Define and add to the list.
  sli = {
    "sli": sli_name,
    "displayName": sli_display_name,
    "key_sli": key_sli,
    "weight": sli_weight
  }

  if pass_thresholds is not None and len(pass_thresholds) > 0:
    sli['pass'] = {
      "criteria": pass_thresholds
    }
  if warning_thresholds is not None and len(warning_thresholds) > 0:
    sli['warning'] = {
      "criteria": warning_thresholds
    }

  sli_list.append(sli)
  count += 1

# Should we compare against a single result or multiple previous runs
compare_against_multiple = input(f"Should Keptn evaluate against multiple previous results? (defaults to a single previous result): ")
if compare_against_multiple != "":
  compare_against_multiple = "several_results"

  # Set the number of comparison results
  number_of_comparison_results = None
  while number_of_comparison_results is None:
    try:
      number_of_comparison_results = input(f"How many previous results should be compared? Defaults to 1: ")
      if number_of_comparison_results == "": number_of_comparison_results = 1
      number_of_comparison_results = int(number_of_comparison_results)
    except:
      number_of_comparison_results: None
      print(f"Please enter a number (not a string) for how many previous results you'd like to compare. Try again...")
  slo_definition['comparison']['number_of_comparison_results'] = number_of_comparison_results
else:
  slo_definition['comparison']['compare_with'] = "single_result"
  slo_definition['comparison']['number_of_comparison_results'] = 1

  
# Include which results in comparison results
# 'all' (the default), only previous passing results: 'pass' or both passing and warning results (pass_or_warn)
include_result_with_score = input(f"Include which results for evaluation purposes? Optional (defaults to all). Use 'all', 'pass' or 'pass_or_warn': ")
if include_result_with_score == "": include_result_with_score = "all"
slo_definition['comparison']['include_result_with_score'] = include_result_with_score

aggregate_function = input(f"Which aggregation should be used for comparisons? Optional (defaults to avg). Use avg, min or max: ")
if aggregate_function == "": aggregate_function = "avg"
slo_definition['comparison']['aggregate_function'] = aggregate_function

# Add slos to definition
slo_definition['objectives'] = sli_list

# Done. Print output
print('\n')
print('Output follows. Save this as slo.yaml')
print('Upload this to Git to the relevant: <stageName>/<serviceName>/slo.yaml')
print('Alternatively, upload using keptn cli: keptn add-resource --project=<projectName> --stage=<stageName> --service=<serviceName> --resource=slo.yaml --resourceUri=slo.yaml')
print('\n\n')
print('---')
print(yaml.dump(slo_definition))
print('\n')
