import json

filepath = '/Users/weijian/Desktop/develop/custom-skills/registry/skills.json'
data = json.load(open(filepath, 'r'))

# Remove skills-sh-installer entry
data = [s for s in data if s['id'] != 'skills-sh-installer']

json.dump(data, open(filepath, 'w'), indent=2, ensure_ascii=False)
print(f'Registry updated, now {len(data)} skills')
