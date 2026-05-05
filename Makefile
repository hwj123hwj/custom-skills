.PHONY: registry validate

registry:
	cd web && npm run generate:registry

validate:
	cd web && npm run validate:registry
