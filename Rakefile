require 'html-proofer'

namespace :site do
  task :build do
    sh "#{RbConfig.ruby} -S jekyll build"
  end

  task :validate do
    sh "python3 -m unittest tests/test_check_site.py"
    sh "python3 scripts/check_site.py --site _site"
    options = { :assume_extension => true, :only_4xx => true, :allow_hash_href => true}
    HTMLProofer.check_directory("./_site", options).run
  end

  task :test => [:build, :validate]
end

task :test do
  Rake::Task["site:test"].invoke
end

desc "Run read-only checks against the production website"
task :smoke do
  sh "python3 scripts/smoke_site.py"
end
