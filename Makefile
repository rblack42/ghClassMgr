test:
	cd code && nosetests

.PHONY: docs
docs:
	cd docs && make html

clean:
	cd docs && make clean

