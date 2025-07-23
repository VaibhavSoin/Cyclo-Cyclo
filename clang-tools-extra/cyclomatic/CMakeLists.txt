add_clang_tool(cyclomatic
  Cyclomatic.cpp
)

target_link_libraries(cyclomatic
  PRIVATE
  clangAST
  clangASTMatchers
  clangFrontend
  clangTooling
)
