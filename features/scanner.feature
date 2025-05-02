Feature: Packfile corruption detection

  Background:
    Given a repository with a packfile "fixtures/pack-corrupt.git"

  Scenario: Corrupted blob in packfile
    When I run "guardian scan fixtures/pack-corrupt.git"
    Then the exit code should be 2
     And the output should contain "Invalid CRC at offset"