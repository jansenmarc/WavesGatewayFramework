import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  Validators
} from '@angular/forms';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/catch';
import 'rxjs/add/observable/throw';
import 'rxjs/add/observable/of';
import { PublicConfigurationService } from '../shared/public.configuration.service';
import { PublicConfiguration } from '../shared/public-configuration.model';
import { RestService } from '../shared/rest.service';
import { TransactionAttemptList } from '../shared/attempt-list.model';
import { ActivatedRoute, Params, Router } from '@angular/router';

@Component({
  selector: 'app-coin-transaction-query',
  templateUrl: './attempt-list-query.component.html',
  styleUrls: ['./attempt-list-query.component.scss']
})
export class AttemptListQueryComponent implements OnInit {
  searchForm: FormGroup;
  asyncResults: Observable<TransactionAttemptList[]>;
  publicConfiguration: PublicConfiguration;

  constructor(
    private restService: RestService,
    private fb: FormBuilder,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    publicConfigurationService: PublicConfigurationService
  ) {
    this.searchForm = fb.group({
      search: [
        '',
        [Validators.compose([Validators.required, Validators.minLength(5)])]
      ]
    });

    this.publicConfiguration = publicConfigurationService.configuration;
  }

  parseQueryParams(params: Params) {
    if (params.anything && params.anything !== this.searchControl.value) {
      this.searchControl.patchValue(params.anything);
    }
  }

  performQuery() {
    this.asyncResults = this.restService.queryAttemptList({
      anything: this.searchControl.value
    });
  }

  ngOnInit(): void {
    this.parseQueryParams(this.activatedRoute.snapshot.queryParams);
    this.activatedRoute.queryParams.subscribe(params => {
      this.parseQueryParams(params);

      if (this.searchForm.valid) {
        this.performQuery();
      }
    });

    if (this.searchForm.valid) {
      this.performQuery();
    }
  }

  get searchControl(): AbstractControl {
    return this.searchForm.get('search');
  }

  onSearchFormSubmit() {
    this.router.navigate(['attempt-list-query'], {
      queryParams: { anything: this.searchControl.value }
    });
  }
}
