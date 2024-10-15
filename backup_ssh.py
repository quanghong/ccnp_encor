import ansible_runner

def run_ansible_playbook(playbook_path, inventory_path):
    # Run the playbook using ansible-runner
    result = ansible_runner.run(
        playbook=playbook_path,
        inventory=inventory_path
    )

    # Display the status of the playbook execution
    if result.rc == 0:
        print("Playbook ran successfully!")
        print("Output:", result.stdout)
    else:
        print("Playbook failed with errors!")
        print("Errors:", result.stderr)

# Specify the path to your playbook and inventory file
playbook_path = '/playbook/backup_config.yml'
inventory_path = 'BSCI_EIGRP/inventory/inventory'


# Run the playbook to backup device configurations
run_ansible_playbook(playbook_path, inventory_path)
