import os
import re

class GitIgnore:
    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)
        self.rules = []
        
        gitignore_path = os.path.join(self.base_dir, ".gitignore")
        if os.path.isfile(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        
                        negated = False
                        if line.startswith("!"):
                            negated = True
                            line = line[1:]
                            
                        is_dir_only = line.endswith("/")
                        if is_dir_only:
                            line = line[:-1]
                            
                        regex = self._pattern_to_regex(line)
                        if regex:
                            self.rules.append((regex, negated, is_dir_only))
            except Exception as e:
                print(f"Warning: Failed to read .gitignore: {e}")

    def _pattern_to_regex(self, pattern: str) -> re.Pattern:
        relative = False
        if pattern.startswith("/"):
            relative = True
            pattern = pattern[1:]
        elif "/" in pattern:
            relative = True

        escaped = re.escape(pattern)
        
        # Replace **/ with (?:.*/)?
        regex_str = escaped.replace(r'\*\*/', '(?:.*/)?')
        # Replace ** with .*
        regex_str = regex_str.replace(r'\*\*', '.*')
        # Replace * with [^/]*
        regex_str = regex_str.replace(r'\*', '[^/]*')
        # Replace ? with [^/]
        regex_str = regex_str.replace(r'\?', '[^/]')
        
        if relative:
            regex_str = "^" + regex_str
        else:
            regex_str = "(^|/)" + regex_str
            
        regex_str = regex_str + "(/|$)"
        
        try:
            return re.compile(regex_str)
        except Exception:
            return None

    def is_ignored(self, path: str, is_dir: bool = False) -> bool:
        # Compute relative path from base_dir
        rel_path = os.path.relpath(path, self.base_dir)
        if rel_path == "." or rel_path.startswith(".."):
            return False
        
        # Normalize path to use forward slash
        rel_path = rel_path.replace(os.sep, "/")
        
        parts = rel_path.split("/")
        current = ""
        for i, part in enumerate(parts):
            if current:
                current = current + "/" + part
            else:
                current = part
                
            current_is_dir = (i < len(parts) - 1) or is_dir
            if self._is_path_ignored_directly(current, current_is_dir):
                return True
        return False

    def _is_path_ignored_directly(self, rel_path: str, is_dir: bool) -> bool:
        ignored = False
        for regex, negated, is_dir_only in self.rules:
            if is_dir_only and not is_dir:
                continue
            
            if regex.search(rel_path):
                ignored = not negated
        return ignored
