require 'html-proofer'

task :test do
  sh "#{RbConfig.ruby} -S jekyll build"
  sh "python3 scripts/check_site.py"
  options = { :assume_extension => true, :only_4xx => true, :allow_hash_href => true}
  HTMLProofer.check_directory("./_site", options).run
end
