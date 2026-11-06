require 'html-proofer'

namespace :site do
  task :build do
    sh "#{RbConfig.ruby} -S jekyll build"
  end

  task :validate do
    sh "python3 -m unittest tests/test_check_site.py"
    sh "python3 scripts/check_site.py --site _site"
    # External availability is checked separately by the advisory monitor. New
    # canonical URLs legitimately return 404 until this artifact is deployed.
    options = { :assume_extension => true, :disable_external => true, :allow_hash_href => true }
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
