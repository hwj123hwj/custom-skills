.PHONY: registry validate add

registry:
	cd web && npm run generate:registry

validate:
	cd web && npm run validate:registry

# 生成 + 验证 + 暂存所有必须提交的生成文件，之后直接 git commit 即可
add: registry validate
	git add registry/skills.json web/src/data/skills-data.json README.md web/public/sitemap.xml
