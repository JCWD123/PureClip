#!/usr/bin/env bash
# File: redirect_repos.sh
# 用法: ./redirect_repos.sh [项目根目录]
set -euo pipefail                                ### CHANGE: 开启严格模式
export GIT_TRACE_PERFORMANCE=1                   ### CHANGE: 若想看 Git 每步耗时，可注释掉

################################
# 配置区域
################################
NEW_DOMAIN="github.com"
ORG_NAME="JCWD123"

STANDARD_IGNORE_RULES=(
  "# IDE files"
  ".idea/"
  ".vscode/"
  "*.code-workspace"

  "# Python compiled files"
  "__pycache__/"
  "*.py[cod]"
  "*.pyd"

  "# Jupyter Notebook checkpoints"
  ".ipynb_checkpoints/"

  "# Log files"
  "logs/"
  "*.log"

  "# Environment variables"
  ".env"
  ".env.local"
  ".secret"

  "# OS generated files"
  ".DS_Store"
  "Thumbs.db"

  "# Coverage files"
  ".coverage"
  "htmlcov/"
)

################################
# 函数定义
################################
info(){ printf "\033[1;32m%s\033[0m\n" "$*"; }
warn(){ printf "\033[1;33m%s\033[0m\n" "$*"; }
err (){ printf "\033[1;31m%s\033[0m\n" "$*" >&2; }

update_gitignore() {
  local gitignore_path="$1/.gitignore"
  [[ -f $gitignore_path ]] || touch "$gitignore_path"

  if ! grep -q "# Standard Git Ignore Rules" "$gitignore_path"; then
    printf "\n# Standard Git Ignore Rules\n# Added by automated redirect script\n" >> "$gitignore_path"
  fi

  for rule in "${STANDARD_IGNORE_RULES[@]}"; do
    grep -qxF "$rule" "$gitignore_path" || echo "$rule" >> "$gitignore_path"
  done
}

untrack_files() {
  info "🗑️  Untracking files ignored by .gitignore ..."
  # 1) deinit 子模块，保证不会卡住
  git submodule deinit -f . >/dev/null 2>&1 || true   ### CHANGE
  # 2) 让 git 自己枚举需要删除的索引项
  git ls-files -z --cached --exclude-standard -i \
    | xargs -0 --no-run-if-empty git rm --cached -q
}

process_repo() {
  local repo_dir="$1"
  info "📦 处理仓库: $repo_dir"
  cd "$repo_dir" || { err "❌ 无法进入目录: $repo_dir"; return 1; }

  # WSL 下放在 /mnt/* 可能会很慢，提醒一下
  [[ $PWD == /mnt/* ]] && warn "⚠️ 仓库位于 /mnt，IO 可能较慢…"

  local project_name
  project_name=$(basename "$PWD")
  local repo_url="git@${NEW_DOMAIN}:${ORG_NAME}/${project_name// /-}.git"
  info "🔗 新仓库地址: $repo_url"

  [[ -d .git ]] || { info "🆕 初始化 Git 仓库"; git init; }

  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "$repo_url"

  git config user.name  "$ORG_NAME"
  git config user.email "${ORG_NAME}@users.noreply.${NEW_DOMAIN}"

  info "🛡️  更新 .gitignore"
  update_gitignore "$PWD"

  untrack_files                               ### CHANGE: 调用新函数

  git add --all
  info "💾 提交更改"
  git commit -m "仓库迁移: 更新忽略规则，清理无用文件" --allow-empty

  info "🚀 推送到新仓库"
  git branch -M main  >/dev/null 2>&1 || true

  if ! git push -u origin main --force; then
    warn "⚠️ 推送失败! 可能的原因:"
    warn "   1. 仓库尚未在 ${NEW_DOMAIN} 创建"
    warn "   2. SSH密钥未配置或无权限"
    warn "   请手动创建仓库: https://${NEW_DOMAIN}/${ORG_NAME}/${project_name// /-}"
    warn "   SSH地址: $repo_url"
    cd - >/dev/null || true
    return 1
  fi
  cd - >/dev/null || true
  info "✅ 完成处理: $project_name\n"
}

find_projects() {
  local base_dir="${1:-$PWD}"
  info "🔍 在目录中搜索项目: $base_dir"

  find "$base_dir" -maxdepth 2 -type d -name '.git' -print0 |
  while IFS= read -r -d '' gitdir; do
    local dir="${gitdir%/.git}"
    [[ $dir =~ /vendor/ || $dir =~ /node_modules/ ]] && continue
    process_repo "$dir"
  done
}

main() {
  info "🚩 开始仓库重定向与清理"
  echo   "========================================"
  echo   "⚙️ 配置:"
  echo   " - 组织名: $ORG_NAME"
  echo   " - 域名  : $NEW_DOMAIN"
  echo   "========================================"

  if (( $# )); then
    for project in "$@"; do
      [[ -d $project ]] && process_repo "$project" || err "❌ 目录不存在: $project"
    done
  else
    find_projects "."
  fi
  echo "========================================"
  info "🎉 所有仓库处理完成！"
}

################################
# 执行入口
################################
main "$@"
