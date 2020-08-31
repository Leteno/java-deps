# java-deps

> A tool to analyze the java deps of java files

Such as: `python java-deps.py <java files/folders>`

Return:
```
{
    "DEPS": {
        "com.android.test.Student": {
            "file": "java-deps/test/Student.java",
            "functions": {
                "void-sayHello-string": {
                    "name": "sayHello",
                    "dependency": {
                        "java.lang.System": {
                            "methods": {
                                "void-print-string"
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Steps:

[ ] Parser: from file to AST
[ ] Analyzer: build DEPS map from AST
[ ] Query: given a invoked function => effected invoker.