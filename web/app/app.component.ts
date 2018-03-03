import { Component } from '@angular/core';
import { PublicConfiguration } from './shared/public-configuration.model';
import { PublicConfigurationService } from './shared/public.configuration.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Params, Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  configuration: PublicConfiguration;
  searchForm: FormGroup;

  constructor(
    publicConfigurationService: PublicConfigurationService,
    fb: FormBuilder,
    private router: Router
  ) {
    this.configuration = publicConfigurationService.configuration;
    this.searchForm = fb.group({
      search: [
        '',
        Validators.compose([Validators.required, Validators.minLength(4)])
      ]
    });
  }

  onSearchFormSubmit() {
    this.router.navigate(['attempt-list-query'], {
      queryParams: { anything: this.searchForm.get('search').value }
    });
  }
}
