#include "clang/AST/AST.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "llvm/Support/raw_ostream.h"
#include <vector>
#include <string>
#include <fstream>  

using namespace clang;
using namespace clang::tooling;


std::vector<std::pair<std::string, int>> results;

class CyclomaticVisitor : public RecursiveASTVisitor<CyclomaticVisitor> {
public:
  explicit CyclomaticVisitor(ASTContext *Context) : Context(Context) {}

  bool VisitFunctionDecl(FunctionDecl *F) {
    if (F->hasBody()) {
      int complexity = 1;
      Stmt *Body = F->getBody();

      for (auto it = Body->child_begin(); it != Body->child_end(); ++it) {
        if (*it) {
          complexity += countBranches(*it);
        }
      }

      std::string funcName = F->getNameInfo().getName().getAsString();
      results.emplace_back(funcName, complexity);
    }
    return true;
  }

private:
  ASTContext *Context;

  int countBranches(Stmt *stmt) {
    int count = 0;
    if (isa<IfStmt>(stmt) || isa<ForStmt>(stmt) || isa<WhileStmt>(stmt) ||
        isa<CaseStmt>(stmt) || isa<ConditionalOperator>(stmt)) {
      count++;
    }

    for (auto it = stmt->child_begin(); it != stmt->child_end(); ++it) {
      if (*it)
        count += countBranches(*it);
    }

    return count;
  }
};

class CyclomaticConsumer : public ASTConsumer {
public:
  explicit CyclomaticConsumer(ASTContext *Context)
      : Visitor(Context) {}

  void HandleTranslationUnit(ASTContext &Context) override {
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  CyclomaticVisitor Visitor;
};

class CyclomaticAction : public ASTFrontendAction {
public:
  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef) override {
    return std::make_unique<CyclomaticConsumer>(&CI.getASTContext());
  }
};

static llvm::cl::OptionCategory MyToolCategory("cyclomatic options");

int main(int argc, const char **argv) {
  auto ExpectedParser = CommonOptionsParser::create(argc, argv, MyToolCategory);
  if (!ExpectedParser) {
    llvm::errs() << "Error parsing options\n";
    return 1;
  }

  ClangTool Tool(ExpectedParser->getCompilations(), ExpectedParser->getSourcePathList());
  int result = Tool.run(newFrontendActionFactory<CyclomaticAction>().get());

  // Print output to terminal
  for (const auto &entry : results) {
    llvm::outs() << entry.first << " " << entry.second << "\n";
  }

  // Write output to file
  std::ofstream outFile("output.txt");
  if (outFile.is_open()) {
    for (const auto &entry : results) {
      outFile << entry.first << " " << entry.second << "\n";
    }
    outFile.close();
    llvm::outs() << "Results written to output.txt\n";
  } else {
    llvm::errs() << "Error: Could not open output.txt for writing.\n";
  }

  return result;
}
